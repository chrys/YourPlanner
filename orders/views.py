from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, View, TemplateView
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from django.db.models import Q, Prefetch
from django.db import transaction
from django.conf import settings 
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from decimal import Decimal
from .models import Order, OrderItem
from users.models import Customer, Professional, ProfessionalCustomerLink 
from services.models import Service, Item, Price
from packages.models import Template, TemplateItemGroup, TemplateItemGroupItem  # Import Template models (packages)
from .forms import OrderForm, OrderStatusUpdateForm, OrderItemForm
from .mixins import CustomerRequiredMixin, UserCanViewOrderMixin, AdminAccessMixin, CustomerOwnsOrderMixin, UserCanModifyOrderItemsMixin
from services.mixins import PriceFilterByWeddingDateMixin  # CHANGED: Import price filtering mixin

class CustomerServiceItemSelectionView(LoginRequiredMixin, CustomerRequiredMixin, PriceFilterByWeddingDateMixin, View):  # CHANGED: Added mixin
    template_name = 'orders/customer_service_item_selection.html'

    def get_service_and_check_permission(self, request, service_pk):
        """
        Fetches the service and checks if the customer is allowed to order it.
        A customer can order if they are actively linked to the service's professional,
        OR if the service is offered by a 'default' professional.
        """
        service = get_object_or_404(
            Service.objects.select_related('professional__user')
            .prefetch_related(
                Prefetch('items', queryset=Item.objects.filter(is_active=True).prefetch_related(
                    Prefetch('prices', queryset=Price.objects.filter(is_active=True).order_by('amount'))
                ))
            ),
            pk=service_pk,
            is_active=True,
            professional__user__is_active=True
        )

        customer_profile = request.user.customer_profile
        
        is_linked_directly = ProfessionalCustomerLink.objects.filter(
            customer=customer_profile,
            professional=service.professional,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        ).exists()

        is_from_default_professional = hasattr(service.professional, 'default') and service.professional.default

        if not (is_linked_directly or is_from_default_professional):
            messages.error(request, "You are not authorized to order items from this service.")
            return None
        return service

    def get(self, request, service_pk):
        service = self.get_service_and_check_permission(request, service_pk)
        if not service:
            return redirect('core:home')
        
        customer_profile = request.user.customer_profile
        pending_orders = Order.objects.filter(
            customer=customer_profile,
            status=Order.StatusChoices.PENDING
        ).order_by('-created_at')

        if pending_orders.exists():
            order = pending_orders.first()
            if pending_orders.count() > 1:
                pass
        else:
            order = Order.objects.create(
                customer=customer_profile,
                status=Order.StatusChoices.PENDING,
                currency=service.professional.preferred_currency if hasattr(service.professional, 'preferred_currency') and service.professional.preferred_currency else settings.DEFAULT_CURRENCY
            )

        # CHANGED: Filter prices based on customer's wedding date and user type
        items_list = list(service.items.all())  # CHANGED: Convert to list to set attributes
        for item in items_list:
            item.applicable_prices = self.get_filtered_prices_for_customer(
                item.prices.all(),
                customer_profile,
                user=self.request.user,  # CHANGED: Pass user for agent detection
                wedding_date=order.wedding_day if not customer_profile and order.wedding_day else None  # CHANGED: Use order's wedding_day if no customer
            )

        current_quantities = {
            oi.price.pk: oi.quantity
            for oi in OrderItem.objects.filter(order=order)
        }

        context = {
            'service': service,
            'items': items_list,  # CHANGED: Pass filtered items list to template
            'order': order,
            'current_quantities': current_quantities,
            'page_title': f"Select from: {service.title}",
            'customer': customer_profile,  # CHANGED: Add customer to context for template

        }
        return render(request, self.template_name, context)

    def post(self, request, service_pk):
        service = self.get_service_and_check_permission(request, service_pk)
        if not service:
            return redirect('core:home')

        customer_profile = request.user.customer_profile
        pending_orders = Order.objects.filter(
            customer=customer_profile,
            status=Order.StatusChoices.PENDING
        ).order_by('-created_at')

        if pending_orders.exists():
            order = pending_orders.first()
            if pending_orders.count() > 1:
                pass
        else:
            order = Order.objects.create(
                customer=customer_profile,
                status=Order.StatusChoices.PENDING,
                currency=service.professional.preferred_currency if hasattr(service.professional, 'preferred_currency') and service.professional.preferred_currency else settings.DEFAULT_CURRENCY
            )

        items_updated_count = 0
        items_added_count = 0
        items_removed_count = 0

        with transaction.atomic():
            for item_in_service in service.items.all():
                for price_in_item in item_in_service.prices.all():
                    quantity_key = f'quantity_price_{price_in_item.pk}'
                    quantity_str = request.POST.get(quantity_key)

                    if quantity_str is None:
                        continue
                    
                    try:
                        quantity = int(quantity_str)
                        if quantity < 0:
                            messages.warning(request, f"Invalid quantity for {price_in_item.item.title}. Quantity set to 0.")
                            quantity = 0
                    except ValueError:
                        messages.warning(request, f"Invalid quantity format for {price_in_item.item.title}. Quantity set to 0.")
                        quantity = 0
                    
                    if quantity > 0:
                        order_item, created = OrderItem.objects.update_or_create(
                            order=order,
                            price=price_in_item,
                            defaults={
                                'quantity': quantity,
                                'item': price_in_item.item,
                                'service': price_in_item.item.service,
                                'professional': price_in_item.item.service.professional,
                                'price_amount_at_order': price_in_item.amount,
                                'price_currency_at_order': price_in_item.currency,
                                'price_frequency_at_order': price_in_item.frequency,
                            }
                        )
                        if created:
                            items_added_count += 1
                        elif order_item.quantity != quantity:
                            items_updated_count += 1
                    else:
                        deleted_count, _ = OrderItem.objects.filter(order=order, price=price_in_item).delete()
                        if deleted_count > 0:
                            items_removed_count += 1
            
            order.calculate_total()
            order.save()

        if items_added_count > 0:
            messages.success(request, f"{items_added_count} item(s) successfully added to your order.")
        if items_updated_count > 0:
            messages.success(request, f"{items_updated_count} item(s) in your order successfully updated.")
        if items_removed_count > 0:
            messages.info(request, f"{items_removed_count} item(s) removed from your order.")
        if not (items_added_count or items_updated_count or items_removed_count):
            messages.info(request, "No changes were made to your order items for this service.")

        return redirect('orders:customer_service_select_items', service_pk=service.pk)


# --- Order CBVs ---

class OrderCreateView(LoginRequiredMixin, CustomerRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.customer = self.request.user.customer_profile
        form.instance.status = Order.StatusChoices.PENDING
        form.instance.total_amount = 0
        messages.success(self.request, "Order created successfully. Now add items to your order.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:select_items', kwargs={'order_pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Create New Order"
        return context


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.all().select_related('customer__user').prefetch_related('items__price__item__service__professional__user')

        if hasattr(user, 'customer_profile') and user.customer_profile:
            queryset = queryset.filter(customer=user.customer_profile)
        elif hasattr(user, 'professional_profile') and user.professional_profile:
            professional = user.professional_profile
            queryset = queryset.filter(items__price__item__service__professional=professional).distinct()
        elif user.is_staff:
            pass
        else:
            return Order.objects.none()

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "My Orders"
        if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile:
            context['page_title'] = "Orders I'm Part Of"
        elif self.request.user.is_staff:
            context['page_title'] = "All Customer Orders"
        return context


class OrderDetailView(LoginRequiredMixin, UserCanViewOrderMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_object(self, queryset=None):
        if hasattr(self, 'order'):
            return self.order
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_items = self.object.items.all().select_related(
            'price__item__service__professional__user',
            'price__item__service',
            'price__item'
        )
        context['order_items'] = order_items
        context['page_title'] = f"Order #{self.object.pk}" 

        context['can_modify_items'] = False
        if self.request.user.is_staff or \
           (hasattr(self.request.user, 'customer_profile') and \
            self.object.customer == self.request.user.customer_profile and \
            self.object.status == Order.StatusChoices.PENDING):
            context['can_modify_items'] = True

        context['can_cancel_order'] = False
        if hasattr(self.request.user, 'customer_profile') and \
           self.object.customer == self.request.user.customer_profile and \
           self.object.status == Order.StatusChoices.PENDING:
            context['can_cancel_order'] = True

        context['can_update_status'] = self.request.user.is_staff

        if context['can_update_status']:
            context['status_update_form'] = OrderStatusUpdateForm(instance=self.object, user=self.request.user)

        # CHANGED: Calculate discount on the fly from rule engine instead of database
        discount_percentage = Decimal('0.00')
        discount_amount = Decimal('0.00')
        discount_description = ''
        
        from rules.engine import process_rules
        discount_info = process_rules(target_entity=self.object, event_code='discount_vip')
        
        if discount_info:
            discount_percentage = discount_info.get('discount_percentage', Decimal('0.00'))
            discount_amount = discount_info.get('discount_amount', Decimal('0.00'))
            discount_description = discount_info.get('discount_description', '')
        
        context['discount_percentage'] = discount_percentage
        context['discount_amount'] = discount_amount
        context['discount_description'] = discount_description

        return context


class OrderStatusUpdateView(LoginRequiredMixin, AdminAccessMixin, UpdateView):
    model = Order
    form_class = OrderStatusUpdateForm
    template_name = 'orders/order_status_update_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f"Order #{self.object.pk} status updated to {self.object.get_status_display()}.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Update Status for Order #{self.object.pk}"
        return context


class OrderCancelView(LoginRequiredMixin, CustomerOwnsOrderMixin, UpdateView):
    model = Order
    template_name = 'orders/order_confirm_cancel.html'
    fields = []

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status=Order.StatusChoices.PENDING)

    def form_valid(self, form):
        if self.object.status != Order.StatusChoices.PENDING:
            messages.error(self.request, "This order can no longer be cancelled.")
            return redirect(self.get_success_url())

        self.object.status = Order.StatusChoices.CANCELLED
        self.object.save()
        messages.success(self.request, f"Order #{self.object.pk} has been cancelled.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_cancellable = self.object.status == Order.StatusChoices.PENDING
        if not is_cancellable:
             messages.warning(self.request, "This order is no longer in a state where it can be cancelled.")
        context['is_cancellable'] = is_cancellable
        context['page_title'] = f"Cancel Order #{self.object.pk}"
        return context


# --- OrderItem CBVs ---

class OrderItemCreateView(LoginRequiredMixin, UserCanModifyOrderItemsMixin, CreateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/orderitem_form.html'
    order_pk_url_kwarg = 'order_pk'

    def dispatch(self, request, *args, **kwargs):
        self.kwargs[UserCanModifyOrderItemsMixin.order_pk_url_kwarg] = self.kwargs['order_pk']
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_instance'] = self.order
        kwargs['available_prices_queryset'] = Price.objects.filter(is_active=True, item__is_active=True, item__service__is_active=True)
        return kwargs

    def form_valid(self, form):
        form.instance.order = self.order

        existing_item = OrderItem.objects.filter(order=self.order, price=form.cleaned_data['price']).first()
        if existing_item:
            existing_item.quantity += form.cleaned_data['quantity']
            existing_item.save()
            self.object = existing_item
            messages.info(self.request, f"Quantity for '{existing_item.price.item.title}' updated in your order.")
        else:
            self.object = form.save()
            messages.success(self.request, f"Item '{self.object.price.item.title}' added to your order.")

        self.order.calculate_total()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.order.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        context['page_title'] = f"Add Item to Order #{self.order.pk_formatted}"
        return context


class OrderItemUpdateView(LoginRequiredMixin, UserCanModifyOrderItemsMixin, UpdateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/orderitem_form.html'
    pk_url_kwarg = 'item_pk'
    order_pk_url_kwarg = 'order_pk'

    def dispatch(self, request, *args, **kwargs):
        self.kwargs[UserCanModifyOrderItemsMixin.order_pk_url_kwarg] = self.kwargs['order_pk']
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return OrderItem.objects.filter(order=self.order, pk=self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_instance'] = self.order
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f"Item '{self.object.price.item.title}' quantity updated.")
        response = super().form_valid(form)
        self.order.calculate_total()
        return response

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.order.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        if self.object:
            context['page_title'] = f"Update Item: {self.object.price.item.title} in Order #{self.order.pk}"
        else:
            context['page_title'] = f"Update Item in Order #{self.order.pk_formatted}"
        return context


class OrderItemDeleteView(LoginRequiredMixin, UserCanModifyOrderItemsMixin, DeleteView):
    model = OrderItem
    template_name = 'orders/orderitem_confirm_delete.html'
    pk_url_kwarg = 'item_pk'
    order_pk_url_kwarg = 'order_pk'
    context_object_name = 'orderitem'

    def dispatch(self, request, *args, **kwargs):
        self.kwargs[UserCanModifyOrderItemsMixin.order_pk_url_kwarg] = self.kwargs['order_pk']
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return OrderItem.objects.filter(order=self.order, pk=self.kwargs.get(self.pk_url_kwarg))
    
    def form_valid(self, form):
        item_title = self.object.price.item.title
        response = super().form_valid(form)
        messages.success(self.request, f"Item '{item_title}' removed from your order.")
        return response

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        self.order.calculate_total()
        return response

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.order.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        context['page_title'] = f"Remove Item from Order #{self.order.pk}"
        return context


# --- Other CBVs (select_items, basket) ---

class SelectItemsView(LoginRequiredMixin, UserCanModifyOrderItemsMixin, PriceFilterByWeddingDateMixin, View):  # CHANGED: Added mixin
    template_name = 'orders/select_items.html'
    order_pk_url_kwarg = 'order_pk'

    def dispatch(self, request, *args, **kwargs):
        self.kwargs[UserCanModifyOrderItemsMixin.order_pk_url_kwarg] = self.kwargs['order_pk']
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        customer = self.order.customer
        
        # Support agent-created orders (no customer) using professional from session
        if customer:
            linked_professionals = Professional.objects.filter(
                customer_links__customer=customer,  
                customer_links__status=ProfessionalCustomerLink.StatusChoices.ACTIVE  
            )
        elif 'temp_professional_id' in self.request.session:
            # For agent-created orders, use professional from session
            linked_professionals = Professional.objects.filter(
                pk=self.request.session['temp_professional_id']
            )
        else:
            linked_professionals = Professional.objects.none()
        
        services_qs = Service.objects.filter(
            is_active=True,
            professional__in=linked_professionals,
            professional__user__is_active=True
        ).prefetch_related(
            Prefetch('items', queryset=Item.objects.filter(is_active=True)
                .prefetch_related(
                    Prefetch('prices', 
                        queryset=Price.objects.filter(is_active=True).order_by('amount')
                    )
                )
            )
        ).order_by('title')

        services_list = []
        for service in services_qs:
            service_dict = {
                'id': service.pk,
                'title': service.title,
                'professional_name': service.professional.title or service.professional.user.get_full_name(),
                'items': []
            }
            for item in service.items.all():
                # CHANGED: Filter prices by customer's wedding date and user type (agent or customer)
                # CHANGED: For agent-created orders (no customer), use order.wedding_day
                filtered_prices = self.get_filtered_prices_for_customer(
                    item.prices.all(),
                    customer,
                    user=self.request.user,  # CHANGED: Pass user for agent detection
                    wedding_date=self.order.wedding_day if not customer and self.order.wedding_day else None  # CHANGED: Use order's wedding_day for agent orders
                )
                
                item_dict = {
                    'id': item.pk,
                    'title': item.title,
                    'description': item.description,
                    'image_url': item.image.url if item.image else None,
                    'prices': []
                }
                # CHANGED: Only include filtered prices
                for price in filtered_prices:
                    item_dict['prices'].append({
                        'id': price.pk,
                        'amount': str(price.amount),
                        'currency': price.currency,
                        'frequency': price.get_frequency_display(),
                        'description': price.description,
                    })
                service_dict['items'].append(item_dict)
            services_list.append(service_dict)

        # Add templates/packages to the selection for agents
        templates_qs = Template.objects.filter(
            professional__in=linked_professionals
        ).prefetch_related(
            Prefetch('item_groups', 
                queryset=TemplateItemGroup.objects.prefetch_related(
                    Prefetch('items',
                        queryset=TemplateItemGroupItem.objects.select_related('item')
                    )
                ).order_by('position')
            )
        ).order_by('title')

        templates_list = []
        for template in templates_qs:
            # Include item groups in template for selection
            item_groups = []
            for group in template.item_groups.all():
                group_dict = {
                    'id': group.pk,
                    'name': group.name,
                    'mandatory_count': group.mandatory_count,
                    'items': []
                }
                for group_item in group.items.all():
                    item_dict = {
                        'id': group_item.item.pk,
                        'title': group_item.item.title,
                        'description': group_item.item.description,
                    }
                    group_dict['items'].append(item_dict)
                item_groups.append(group_dict)
            
            template_dict = {
                'id': f'template_{template.pk}',  # Prefix to distinguish from service items
                'title': template.title,
                'description': template.description,
                'professional_name': template.professional.title or template.professional.user.get_full_name(),
                'base_price': str(template.base_price),
                'currency': template.currency,
                'default_guests': template.default_guests,
                'price_per_additional_guest': str(template.price_per_additional_guest),
                'is_template': True,  # Flag to identify as template
                'item_groups': item_groups  # Include item groups for selection
            }
            templates_list.append(template_dict)

        current_quantities_dict = {
            item.price.pk: item.quantity
            for item in OrderItem.objects.filter(order=self.order)
        }

        context = {
            'order': self.order,
            'services_json': json.dumps(services_list),
            'templates_json': json.dumps(templates_list),  # Add templates to context
            'current_quantities_json': json.dumps(current_quantities_dict),
            'page_title': f"Select Items for Order #{self.order.pk}",
        }
        context.update(kwargs)
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        quantities = {}
        items_to_delete = []
        templates_to_add = {}  # Store template selections
        template_guest_counts = {}  # Store guest counts per template

        import sys  # Debug logging
        print(f"DEBUG: POST data keys: {list(request.POST.keys())}", file=sys.stderr)  # Log all keys
        print(f"DEBUG: POST data: {dict(request.POST)}", file=sys.stderr)  # Log all data

        for key, value in request.POST.items():
            # Handle guest count inputs (format: guest_count_template_<pk>)
            if key.startswith('guest_count_'):
                try:
                    id_part = key.replace('guest_count_', '')  # Remove prefix to get template_<pk> format
                    if id_part.startswith('template_'):
                        template_id = int(id_part.replace('template_', ''))
                        guest_count = int(value)
                        template_guest_counts[template_id] = guest_count
                        print(f"DEBUG: Parsed guest_count for template {template_id}: {guest_count}", file=sys.stderr)  # Debug
                except (ValueError, IndexError) as e:
                    print(f"DEBUG: Error parsing guest_count {key}={value}: {e}", file=sys.stderr)  # Debug
                    pass
            elif key.startswith('quantity_'):
                try:
                    id_part = key.split('_', 1)[1]  # Split more carefully to handle 'template_' prefix
                    print(f"DEBUG: Processing quantity key={key}, id_part={id_part}, value={value}", file=sys.stderr)  # Debug
                    quantity = int(value)
                    
                    if quantity < 0:
                        messages.error(request, f"Invalid quantity. Quantity must be non-negative.")
                        continue

                    if id_part.startswith('template_'):  # Handle template IDs
                        # Template ID format: template_<pk>
                        template_id = int(id_part.replace('template_', ''))
                        if quantity > 0:
                            templates_to_add[template_id] = quantity
                            print(f"DEBUG: Added template {template_id} with quantity {quantity}", file=sys.stderr)  # Debug
                    else:  # Regular service price ID
                        price_id = int(id_part)
                        if quantity > 0:
                            quantities[price_id] = quantity
                        else:
                            items_to_delete.append(price_id)
                except (ValueError, IndexError) as e:
                    print(f"DEBUG: Error parsing quantity {key}={value}: {e}", file=sys.stderr)  # Debug error
                    messages.error(request, f"Invalid data submitted: {e}")
                    return render(request, self.template_name, self.get_context_data(error="Invalid data."))

        with transaction.atomic():
            # Process templates first
            for template_id, quantity in templates_to_add.items():
                try:
                    template = get_object_or_404(Template, pk=template_id)
                    # Set template on order (only one template per order)
                    self.order.template = template
                    
                    # Use guest count from form or default
                    guest_count = template_guest_counts.get(template_id, template.default_guests)
                    self.order.template_guest_count = guest_count
                    
                    # Calculate total = base_price + (additional_guests * price_per_additional_guest)
                    additional_guests = max(0, guest_count - template.default_guests)
                    calculated_total = template.base_price + (additional_guests * template.price_per_additional_guest)
                    self.order.template_total_amount = calculated_total
                    
                    messages.success(request, f"Added package '{template.title}' ({guest_count} guests) to your order.")
                except Template.DoesNotExist:
                    messages.error(request, f"Package not found.")
                    return render(request, self.template_name, self.get_context_data(error="Invalid package."))

            for price_id, quantity in quantities.items():
                price = get_object_or_404(Price, pk=price_id, is_active=True, item__is_active=True, item__service__is_active=True)
                order_item, created = OrderItem.objects.update_or_create(
                    order=self.order,
                    price=price,
                    defaults={
                        'quantity': quantity,
                        'item': price.item,
                        'service': price.item.service,
                        'professional': price.item.service.professional,
                        'price_amount_at_order': price.amount,
                        'price_currency_at_order': price.currency,
                        'price_frequency_at_order': price.frequency,
                    }
                )
                if created:
                    messages.success(request, f"Added '{price.item.title}' (x{quantity}) to your order.")
                elif order_item.quantity != quantity:
                    messages.info(request, f"Updated quantity for '{price.item.title}' to {quantity}.")
            
            if items_to_delete:
                deleted_count, _ = OrderItem.objects.filter(order=self.order, price_id__in=items_to_delete).delete()
                if deleted_count > 0:
                    messages.info(request, f"Removed {deleted_count} item(s) from your order as quantity was set to 0.")

            # Recalculate order total to include BOTH template and add-on items
            if self.order.template:  # If order has template
                # Calculate add-ons total from items
                add_ons_total = Decimal('0.00')
                for item in self.order.items.all():
                    add_ons_total += (item.price_amount_at_order or Decimal('0.00')) * (item.quantity or 0)
                
                # Grand total = template + add-ons
                self.order.total_amount = (self.order.template_total_amount or Decimal('0.00')) + add_ons_total
            else:  # No template, just sum items
                self.order.calculate_total()
            
            self.order.save(update_fields=['total_amount', 'template', 'template_guest_count', 'template_total_amount'])  # Save template fields too

        return redirect('orders:order_detail', pk=self.order.pk)

class BasketView(LoginRequiredMixin, CustomerRequiredMixin, TemplateView):
    template_name = 'orders/basket.html'

    def get_context_data(self, **kwargs):
        # Retrieve context from parent
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer_profile
        #  Get pending order or None
        current_order = Order.objects.filter(customer=customer, status=Order.StatusChoices.PENDING).first()

        #  Initialize empty list
        order_items_with_details = []
        #  Only fetch items if order exists
        if current_order:
            order_items_with_details = current_order.items.all().select_related(
                'price__item__service__professional__user',
                'price__item__service',
                'price__item'
            ).order_by('price__item__service__title', 'price__item__title')

        #  Add order to context (can be None)
        context['order'] = current_order
        #  Add order items to context
        context['order_items'] = order_items_with_details
        
        add_ons_total = Decimal('0.00')
        if current_order:
            for item in current_order.items.all():
                add_ons_total += (item.price_amount_at_order or Decimal('0.00')) * (item.quantity or 0)
        
        context['add_ons_total'] = add_ons_total
        
        # Changed: Calculate discount on the fly from rule engine instead of database
        discount_percentage = Decimal('0.00')
        discount_amount = Decimal('0.00')
        discount_description = ''
        grand_total = current_order.total_amount if current_order else Decimal('0.00')
        
        if current_order:
            from rules.engine import process_rules
            discount_info = process_rules(target_entity=current_order, event_code='discount_vip')
            
            if discount_info:
                discount_percentage = discount_info.get('discount_percentage', Decimal('0.00'))
                discount_amount = discount_info.get('discount_amount', Decimal('0.00'))
                discount_description = discount_info.get('discount_description', '')
                grand_total = discount_info.get('final_total', current_order.total_amount)
        
        context['discount_percentage'] = discount_percentage
        context['discount_amount'] = discount_amount
        context['discount_description'] = discount_description
        context['grand_total'] = grand_total
        
        context['page_title'] = "My Basket"
        return context


#  Moved update_template_guests outside of BasketView class as module-level function
# ...existing code...

@require_POST  #  Ensure decorator is present
@login_required  #  Ensure decorator is present
def update_template_guests(request, pk):  #  Ensure function signature matches URL pattern
    """ Update guest count for a template-based order and recalculate total."""
    order = get_object_or_404(Order, pk=pk)
    
    #  Check permissions
    if not hasattr(request.user, 'customer_profile') or order.customer != request.user.customer_profile:
        messages.error(request, "You do not have permission to modify this order.")
        return redirect('orders:basket')  #  Redirect to basket instead of order_detail
    
    #  Check if order has a template
    if not order.template:
        messages.error(request, "This order does not have a package.")
        return redirect('orders:basket')  #  Redirect to basket
    
    #  Parse and validate guest count
    try:
        guest_count = int(request.POST.get('guest_count', order.template.default_guests))
        if guest_count < order.template.default_guests:
            messages.error(request, f"Guest count must be at least {order.template.default_guests}.")
            return redirect('orders:basket')  #  Redirect to basket
    except (ValueError, TypeError):  #  Added TypeError
        messages.error(request, "Invalid guest count.")
        return redirect('orders:basket')  #  Redirect to basket
    
    #  Recompute template total
    additional_guests = max(0, guest_count - (order.template.default_guests or 0))
    template_total = (order.template.base_price or Decimal('0.00')) + (order.template.price_per_additional_guest or Decimal('0.00')) * Decimal(additional_guests)
    
    #  Update order
    order.template_guest_count = guest_count
    order.template_total_amount = template_total
    
    #  Recompute grand total (template + add-ons)
    add_ons_total = Decimal('0.00')
    for item in order.items.all():
        add_ons_total += (item.price_amount_at_order or Decimal('0.00')) * (item.quantity or 0)
    
    order.total_amount = template_total + add_ons_total
    order.save()  #  Ensure save is called
    
    messages.success(request, f"Package updated for {guest_count} guests. New total: {order.total_amount} {order.currency}.")  #  Show success message
    return redirect('orders:basket')  #  Redirect back to basket to see updated values
# ...existing code...

#  Moved remove_template outside of BasketView class as module-level function
@require_POST
@login_required
def remove_template(request):
    """ Remove template snapshot from order. Keep add-on items."""
    user = request.user
    if not hasattr(user, 'customer_profile'):
        messages.error(request, "You need a customer profile to modify the basket.")
        return redirect('users:user_management')

    customer = user.customer_profile
    order = Order.objects.filter(customer=customer, status=Order.StatusChoices.PENDING).order_by('-updated_at').first()
    
    if not order or not order.template:
        messages.info(request, "No package in your basket to remove.")
        return redirect('orders:basket')

    #  Clear template snapshot
    order.template = None
    order.template_guest_count = 0
    order.template_total_amount = None

    #  Recalculate total from add-on items only
    add_ons_total = Decimal('0.00')
    for item in order.items.all():
        add_ons_total += (item.price_amount_at_order or Decimal('0.00')) * (item.quantity or 0)
    
    order.total_amount = add_ons_total
    order.save(update_fields=['template', 'template_guest_count', 'template_total_amount', 'total_amount'])

    messages.success(request, "Package removed from your basket.")
    return redirect('orders:basket')