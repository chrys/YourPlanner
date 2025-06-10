from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, View, TemplateView
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden, HttpResponseNotFound # HttpResponseForbidden might be useful, Added HttpResponseNotFound
from django.db.models import Q, Prefetch # For complex queries in OrderListView, Added Prefetch
from django.shortcuts import render # Added render for SelectItemsView GET
from django.db import transaction
import json # Moved json import to the top
from django.http import JsonResponse
from django.urls import reverse
from users.views import AgentRequiredMixin # For API View

from .models import Order, OrderItem
from users.models import Customer, Professional, ProfessionalCustomerLink 
from services.models import Service, Item, Price # For select_items and OrderItemForm population
from .forms import OrderForm, OrderStatusUpdateForm, OrderItemForm

# --- Authorization Mixins ---

class CustomerRequiredMixin(UserPassesTestMixin):
    """Ensures the logged-in user has a customer profile."""
    def test_func(self):
        try:
            # Check if profile exists and is not None
            return hasattr(self.request.user, 'customer_profile') and self.request.user.customer_profile is not None
        except Customer.DoesNotExist: # This exception might not be directly raised by hasattr
            return False
        except AttributeError: # If user is AnonymousUser which has no customer_profile
            return False


    def handle_no_permission(self):
        messages.error(self.request, "You need a customer profile to access this page.")
        return redirect('users:profile_choice') # Or 'users:customer_profile_create'


class AdminAccessMixin(UserPassesTestMixin):
    """Ensures the logged-in user is a staff member."""
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access this page.")
        if self.request.user.is_authenticated:
            return redirect('/')
        return redirect('users:login') # Assuming 'users:login'


class CustomerOwnsOrderMixin(UserPassesTestMixin):
    """
    Ensures the current customer owns the order. Loads self.order.
    Assumes 'pk' or 'order_pk' is in self.kwargs for the order's primary key.
    """
    order_pk_url_kwarg = 'pk'

    def test_func(self):
        order_id = self.kwargs.get(self.order_pk_url_kwarg)
        if not order_id:
            # This should ideally not be reached if URL patterns are correct
            raise Http404("Order ID not found in URL context.")
        try:
            # Ensure user has a customer profile first
            if not (hasattr(self.request.user, 'customer_profile') and self.request.user.customer_profile):
                return False
            customer = self.request.user.customer_profile
            self.order = get_object_or_404(Order, pk=order_id, customer=customer)
            return True
        except Customer.DoesNotExist: # Should be caught by the hasattr check above
            return False
        except Http404:
            return False # Order not found or not owned by this customer

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to view or modify this order.")
        return redirect('orders:order_list')


class ProfessionalManagesOrderMixin(UserPassesTestMixin):
    """
    Ensures the current professional is associated with the order via an OrderItem.
    Loads self.order. Assumes 'pk' or 'order_pk' is in self.kwargs.
    """
    order_pk_url_kwarg = 'pk'

    def test_func(self):
        order_id = self.kwargs.get(self.order_pk_url_kwarg)
        if not order_id:
            raise Http404("Order ID not found in URL context.")
        try:
            if not (hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile):
                return False
            professional = self.request.user.professional_profile
            self.order = get_object_or_404(Order, pk=order_id) # Fetch the order first

            is_managing = OrderItem.objects.filter(
                order=self.order,
                price__item__service__professional=professional
            ).exists()
            return is_managing
        except Professional.DoesNotExist: # Should be caught by hasattr
            return False
        except Http404:
            return False # Order not found

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to view or manage this order.")
        return redirect('services:service_list') # Redirect to a professional's typical view


class UserCanViewOrderMixin(UserPassesTestMixin):
    """
    Generic mixin to check if a user can view an order.
    Loads self.order. Assumes 'pk' is in self.kwargs.
    """
    def test_func(self):
        order_id = self.kwargs.get('pk')
        if not order_id:
            raise Http404("Order ID not found in URL context.")

        self.order = get_object_or_404(Order, pk=order_id)

        if self.request.user.is_staff:
            return True

        # Check for customer ownership
        if hasattr(self.request.user, 'customer_profile') and self.request.user.customer_profile:
            if self.order.customer == self.request.user.customer_profile:
                return True

        # Check for professional management
        if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile:
            professional = self.request.user.professional_profile
            if OrderItem.objects.filter(order=self.order, price__item__service__professional=professional).exists():
                return True

        return False

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to view this order.")
        if self.request.user.is_authenticated:
            # Determine a sensible redirect based on potential roles
            if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile:
                 return redirect('services:service_list')
            elif hasattr(self.request.user, 'customer_profile') and self.request.user.customer_profile:
                 return redirect('orders:order_list')
            return redirect('/') # Fallback for authenticated users with no clear role page
        return redirect('users:login')


class UserCanModifyOrderItemsMixin(UserPassesTestMixin):
    """
    Checks if the user can modify items for the current order.
    Allowed if:
    1. User is customer owning the order AND order is PENDING.
    2. User is an admin (staff).
    3. User is a Professional linked to the order's Customer.
    Loads self.order. Assumes 'pk' or 'order_pk' is in self.kwargs.
    """
    order_pk_url_kwarg = 'pk'

    def test_func(self):
        order_id = self.kwargs.get(self.order_pk_url_kwarg)
        if not order_id:
            raise Http404("Order ID not found in URL context.")

        # Use select_related to potentially improve efficiency if customer profile is accessed often
        self.order = get_object_or_404(Order.objects.select_related('customer__user'), pk=order_id)

        if self.request.user.is_staff:
            return True

        if hasattr(self.request.user, 'customer_profile') and self.request.user.customer_profile:
            if self.order.customer == self.request.user.customer_profile and self.order.status == Order.StatusChoices.PENDING:
                return True
            
         # Condition for a Professional linked to the order's customer and order is PENDING
        if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile:
            professional = self.request.user.professional_profile
            # Check if an active link exists between this professional and the order's customer
            is_linked_and_active = ProfessionalCustomerLink.objects.filter(
                professional=professional,
                customer=self.order.customer,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            ).exists()

            if is_linked_and_active and self.order.status == Order.StatusChoices.PENDING:
                return True

        return False

    def handle_no_permission(self):
        messages.error(self.request, "Order items cannot be modified for this order at its current status, or you lack permission.")
        # Try to redirect to order detail if order was loaded, otherwise to order list
        order_pk_to_redirect = self.kwargs.get(self.order_pk_url_kwarg)
        if order_pk_to_redirect:
             return redirect('orders:order_detail', pk=order_pk_to_redirect)
        return redirect('orders:order_list')


# --- Order CBVs ---

class OrderCreateView(LoginRequiredMixin, CustomerRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html' # To be created
    
    def form_valid(self, form):
        form.instance.customer = self.request.user.customer_profile
        form.instance.status = Order.StatusChoices.PENDING # Default status
        # Total amount will be calculated as items are added/updated.
        form.instance.total_amount = 0
        messages.success(self.request, "Order created successfully. Now add items to your order.")
        # self.object will be the created order instance
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to select_items view for this newly created order
        return reverse_lazy('orders:select_items', kwargs={'order_pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Create New Order"
        return context


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html' # To be created
    context_object_name = 'orders'
    paginate_by = 10 # Optional pagination

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.all().select_related('customer__user').prefetch_related('items__price__item__service__professional__user')

        if hasattr(user, 'customer_profile') and user.customer_profile:
            # Customer sees their own orders
            queryset = queryset.filter(customer=user.customer_profile)
        elif hasattr(user, 'professional_profile') and user.professional_profile:
            # Professional sees orders they are part of (i.e., containing their services)
            professional = user.professional_profile
            queryset = queryset.filter(items__price__item__service__professional=professional).distinct()
        elif user.is_staff:
            # Admin sees all orders
            pass # No additional filtering needed for admin beyond the base queryset
        else:
            # User has no relevant profile (should ideally not happen if app logic is correct)
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
    template_name = 'orders/order_detail.html' # To be created
    context_object_name = 'order'
    # self.order is loaded by UserCanViewOrderMixin's test_func

    def get_object(self, queryset=None):
        # self.order is already fetched by the UserCanViewOrderMixin.
        # The DetailView's get_object normally fetches it, but we can just return it.
        if hasattr(self, 'order'):
            return self.order
        # Fallback if mixin didn't set it for some reason (should not happen)
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.object is the order instance, also available as self.order via mixin.
        order_items = self.object.items.all().select_related(
            'price__item__service__professional__user',
            'price__item__service',
            'price__item'
        )
        context['order_items'] = order_items
        context['page_title'] = f"Order #{self.object.pk}" 

        # Determine if actions like adding/removing items or cancelling are allowed
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

        context['can_update_status'] = self.request.user.is_staff # Only staff can update status via OrderStatusUpdateView

        # Pass the OrderStatusUpdateForm if user can update status
        if context['can_update_status']:
            context['status_update_form'] = OrderStatusUpdateForm(instance=self.object, user=self.request.user)

        return context


class OrderStatusUpdateView(LoginRequiredMixin, AdminAccessMixin, UpdateView): # Or a more specific Professional role mixin
    model = Order
    form_class = OrderStatusUpdateForm
    template_name = 'orders/order_status_update_form.html' # Can be part of order_detail or standalone
    # pk_url_kwarg = 'pk' (default)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # Pass user to form for dynamic choices
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f"Order #{self.object.pk} status updated to {self.object.get_status_display()}.")
        # Potentially add logic here: send notifications, update stock, etc.
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Update Status for Order #{self.object.pk}"
        return context


class OrderCancelView(LoginRequiredMixin, CustomerOwnsOrderMixin, UpdateView):
    model = Order
    template_name = 'orders/order_confirm_cancel.html' # To be created
    fields = [] # No fields needed from user, just confirmation.
    # self.order is loaded by CustomerOwnsOrderMixin's test_func

    def get_queryset(self):
        # Further restrict to only cancellable orders (e.g., PENDING)
        queryset = super().get_queryset()
        return queryset.filter(status=Order.StatusChoices.PENDING)

    def form_valid(self, form):
        # self.object is the order instance, also self.order
        if self.object.status != Order.StatusChoices.PENDING:
            messages.error(self.request, "This order can no longer be cancelled.")
            return redirect(self.get_success_url())

        self.object.status = Order.StatusChoices.CANCELLED
        self.object.save()
        messages.success(self.request, f"Order #{self.object.pk} has been cancelled.")
        # TODO: Add logic here if needed: e.g., inform professional, revert stock.
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check again if order is cancellable for template display, in case of direct GET access
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
    template_name = 'orders/orderitem_form.html' # To be created
    # order_pk_url_kwarg from UserCanModifyOrderItemsMixin is 'pk' by default,
    # but our URL for creating an OrderItem will likely have 'order_pk'.
    # So, we set it on the view for the mixin to use.
    order_pk_url_kwarg = 'order_pk'


    def dispatch(self, request, *args, **kwargs):
        # UserCanModifyOrderItemsMixin's test_func is called, it loads self.order
        # or denies permission.
        # The 'order_pk' from URL is used by the mixin.
        self.kwargs[UserCanModifyOrderItemsMixin.order_pk_url_kwarg] = self.kwargs['order_pk']
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_instance'] = self.order # self.order is set by UserCanModifyOrderItemsMixin
        # TODO: Define available_prices_queryset more precisely.
        # For now, all active prices. In future, could be filtered by professional or other criteria.
        kwargs['available_prices_queryset'] = Price.objects.filter(is_active=True, item__is_active=True, item__service__is_active=True)
        return kwargs

    def form_valid(self, form):
        form.instance.order = self.order # self.order set by mixin

        # Check if an OrderItem with the same price (and thus same item) already exists for this order
        existing_item = OrderItem.objects.filter(order=self.order, price=form.cleaned_data['price']).first()
        if existing_item:
            existing_item.quantity += form.cleaned_data['quantity']
            existing_item.save()
            self.object = existing_item # Set self.object to the updated item for success message
            messages.info(self.request, f"Quantity for '{existing_item.price.item.title}' updated in your order.")
        else:
            self.object = form.save() # This creates the new OrderItem
            messages.success(self.request, f"Item '{self.object.price.item.title}' added to your order.")

        self.order.calculate_total()
        return redirect(self.get_success_url()) # super().form_valid() normally redirects, but we handle it here due to potential update

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.order.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order # self.order set by mixin
        context['page_title'] = f"Add Item to Order #{self.order.pk_formatted}"
        return context


class OrderItemUpdateView(LoginRequiredMixin, UserCanModifyOrderItemsMixin, UpdateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/orderitem_form.html'
    # pk_url_kwarg for OrderItem is 'item_pk' in URL, order_pk for Order
    pk_url_kwarg = 'item_pk'
    order_pk_url_kwarg = 'order_pk' # For UserCanModifyOrderItemsMixin

    def dispatch(self, request, *args, **kwargs):
        # Ensure the mixin uses the correct kwarg for the order's PK.
        self.kwargs[UserCanModifyOrderItemsMixin.order_pk_url_kwarg] = self.kwargs['order_pk']
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Filter OrderItems to only those belonging to self.order (set by mixin)
        # and matching the item_pk from the URL.
        return OrderItem.objects.filter(order=self.order, pk=self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_instance'] = self.order
        # For updates, the form's __init__ handles disabling the price field
        # and setting its queryset correctly using self.instance.price.
        # So, no need to pass available_prices_queryset here.
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f"Item '{self.object.price.item.title}' quantity updated.")
        response = super().form_valid(form)
        self.order.calculate_total()
        return response

    def get_success_url(self):
        #return reverse_lazy('orders:order_detail', kwargs={'pk': self.order.pk})
        return reverse_lazy('users:customer_basket', kwargs={'order_id': self.order.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        if self.object: # self.object is the OrderItem instance
            context['page_title'] = f"Update Item: {self.object.price.item.title} in Order #{self.order.pk}"
        else:
            context['page_title'] = f"Update Item in Order #{self.order.pk_formatted}"
        return context


class OrderItemDeleteView(LoginRequiredMixin, UserCanModifyOrderItemsMixin, DeleteView):
    model = OrderItem
    template_name = 'orders/orderitem_confirm_delete.html' # To be created
    pk_url_kwarg = 'item_pk'
    order_pk_url_kwarg = 'order_pk' # For UserCanModifyOrderItemsMixin
    context_object_name = 'orderitem'


    def dispatch(self, request, *args, **kwargs):
        self.kwargs[UserCanModifyOrderItemsMixin.order_pk_url_kwarg] = self.kwargs['order_pk']
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return OrderItem.objects.filter(order=self.order, pk=self.kwargs.get(self.pk_url_kwarg))
    
    def form_valid(self, form):
        # Store item title for message before it's deleted
        item_title = self.object.price.item.title
        # super().form_valid(form) would call delete() and then redirect.
        # We need to calculate total *after* deletion.
        # The DeleteView's post method calls delete and then get_success_url.
        # So, we override delete().
        response = super().form_valid(form) # This will call delete() internally
        messages.success(self.request, f"Item '{item_title}' removed from your order.")
        return response

    def delete(self, request, *args, **kwargs):
        # Called by form_valid in DeleteView's default post or by super().form_valid()
        response = super().delete(request, *args, **kwargs)
        self.order.calculate_total() # self.order is set by mixin
        return response

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.order.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order # self.order set by mixin
        context['page_title'] = f"Remove Item from Order #{self.order.pk}"
        return context

# --- Other CBVs (select_items, basket) ---

class SelectItemsView(LoginRequiredMixin, UserCanModifyOrderItemsMixin, View):
    template_name = 'orders/select_items.html' # To be created
    # UserCanModifyOrderItemsMixin uses 'pk' by default for order_pk_url_kwarg
    # Ensure URL for this view uses 'pk' for the order_pk, or override order_pk_url_kwarg here.
    # For consistency with OrderDetailView etc., let's assume the URL will pass 'order_pk'.
    order_pk_url_kwarg = 'order_pk'


    def dispatch(self, request, *args, **kwargs):
        # Ensure the mixin uses the correct kwarg for the order's PK from the URL.
        self.kwargs[UserCanModifyOrderItemsMixin.order_pk_url_kwarg] = self.kwargs['order_pk']
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # self.order is loaded by UserCanModifyOrderItemsMixin
        services_qs = Service.objects.filter(is_active=True, professional__user__is_active=True) \
            .prefetch_related(
                Prefetch('items', queryset=Item.objects.filter(is_active=True)
                    .prefetch_related(Prefetch('prices', queryset=Price.objects.filter(is_active=True).order_by('amount')))
                )
        ).order_by('title')

        services_list = []
        for service in services_qs:
            service_dict = {
                'id': service.pk,
                'title': service.title,
                'items': []
            }
            for item in service.items.all():
                item_dict = {
                    'id': item.pk,
                    'title': item.title,
                    'description': item.description,
                    'image_url': item.image.url if item.image else None,
                    'prices': []
                }
                for price in item.prices.all():
                    item_dict['prices'].append({
                        'id': price.pk,
                        'amount': str(price.amount), # Use string for decimal consistency
                        'currency': price.currency,
                        'frequency': price.get_frequency_display(),
                        'description': price.description,
                    })
                service_dict['items'].append(item_dict)
            services_list.append(service_dict)

        current_quantities_dict = {
            item.price.pk: item.quantity
            for item in OrderItem.objects.filter(order=self.order)
        }

        context = {
            'order': self.order,
            # 'services': services_qs, # Keep original queryset if needed by other parts, though Vue uses JSON
            'services_json': json.dumps(services_list),
            'current_quantities_json': json.dumps(current_quantities_dict),
            'page_title': f"Select Items for Order #{self.order.pk}",
        }
        context.update(kwargs)
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        # self.order is loaded by UserCanModifyOrderItemsMixin
        quantities = {}
        items_to_delete = []

        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                try:
                    price_id = int(key.split('_')[1])
                    quantity = int(value)
                    if quantity < 0: # Should not happen with min=0 on input
                        messages.error(request, f"Invalid quantity for price ID {price_id}. Quantity must be non-negative.")
                        continue # or redirect with error

                    if quantity > 0:
                        quantities[price_id] = quantity
                    else: # quantity is 0, mark for deletion if exists
                        items_to_delete.append(price_id)
                except (ValueError, IndexError):
                    messages.error(request, "Invalid data submitted.")
                    # Consider how to handle this - perhaps render form again with errors
                    return render(request, self.template_name, self.get_context_data(error="Invalid data."))

        with transaction.atomic():
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
                elif order_item.quantity != quantity: # Check if quantity actually changed before messaging
                    messages.info(request, f"Updated quantity for '{price.item.title}' to {quantity}.")
            
            # Delete items where quantity was set to 0
            if items_to_delete:
                deleted_count, _ = OrderItem.objects.filter(order=self.order, price_id__in=items_to_delete).delete()
                if deleted_count > 0:
                    messages.info(request, f"Removed {deleted_count} item(s) from your order as quantity was set to 0.")

            self.order.calculate_total()

        # Redirect to basket or order detail page
        return redirect('orders:order_detail', pk=self.order.pk)


class BasketView(LoginRequiredMixin, CustomerRequiredMixin, TemplateView):
    template_name = 'orders/basket.html' # To be created

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer_profile
        current_order = Order.objects.filter(customer=customer, status=Order.StatusChoices.PENDING).first()

        order_items_with_details = []
        if current_order:
            order_items_with_details = current_order.items.all().select_related(
                'price__item__service__professional__user',
                'price__item__service',
                'price__item'
            ).order_by('price__item__service__title', 'price__item__title')

        context['order'] = current_order
        context['order_items'] = order_items_with_details
        context['page_title'] = "My Basket"
        # Total is on current_order.total_amount, no need to recalculate here if up-to-date
        return context

class AgentOrdersApiView(LoginRequiredMixin, AgentRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        agent_profile = request.user.agent_profile
        # Ensure 'labels' is prefetched if it's a ManyToManyField on Order
        # and 'user' on customer/agent if using their details in __str__ or for currency.
        orders = Order.objects.filter(agent=agent_profile).prefetch_related('labels').order_by('-order_date')

        orders_data = []
        for order in orders:
            labels_data = [{'name': label.name, 'color': label.color, 'text_color': label.text_color}
                           for label in order.labels.all()] # Assuming Label has color and text_color

            # Basic placeholder URLs, these will need actual URL patterns
            # and might need to check permissions if they were real views.
            try:
                edit_url = reverse('users:agent_edit_order', args=[order.pk])
            except Exception: # Catch NoReverseMatch if URL is not yet defined
                edit_url = "#edit-not-defined"

            try:
                # For API delete, it might be a different pattern or handled by the Vue app via POST/DELETE to this API view with ID.
                # This is a placeholder for a GET-based delete URL for simplicity in example data.
                delete_url = reverse('users:agent_delete_order_api', args=[order.pk])
            except Exception:
                delete_url = "#delete-not-defined"

            orders_data.append({
                'id': order.pk,
                'title': str(order),
                'status': order.get_status_display(),
                'status_raw': order.status,
                'total_amount': order.total_amount,
                'currency_symbol': order.currency_display_symbol if hasattr(order, 'currency_display_symbol') else order.currency,
                'order_date': order.order_date.strftime('%Y-%m-%d %H:%M'),
                'labels': labels_data,
                'edit_url': edit_url,
                'delete_url': delete_url
            })
        return JsonResponse({'orders': orders_data})

class AgentDeleteOrderApiView(LoginRequiredMixin, AgentRequiredMixin, View):
    def post(self, request, order_id, *args, **kwargs): # Using POST for simplicity, could be DELETE
        agent_profile = request.user.agent_profile
        order = get_object_or_404(Order, pk=order_id)

        # Check if the agent owns this order
        if order.agent != agent_profile:
            return HttpResponseForbidden(JsonResponse({'success': False, 'error': 'Permission denied.'}))

        # Check if order can be deleted (e.g., only PENDING orders)
        # Example:
        # if order.status != Order.StatusChoices.PENDING:
        #    return JsonResponse({'success': False, 'error': 'Only pending orders can be deleted.'}, status=400)

        try:
            order.delete()
            return JsonResponse({'success': True, 'message': 'Order deleted successfully.'})
        except Exception as e:
            # Log the exception e
            print(f"Error deleting order {order_id} for agent {agent_profile.user.username}: {e}") # Basic logging
            return JsonResponse({'success': False, 'error': 'Failed to delete order.'}, status=500)
