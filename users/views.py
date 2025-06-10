from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.safestring import mark_safe
# from django.core.exceptions import ValidationError # Not used
from django.db import transaction
from django.contrib.auth import login
from django.utils.html import escape
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.views.generic import CreateView, View, TemplateView, FormView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404 # Though DetailView handles its own 404
from django.templatetags.static import static # For placeholder image URL
import json # For serializing data for Vue

from .models import Professional, Customer, Agent, ProfessionalCustomerLink
from templates.models import Template, TemplateImage # For CustomerTemplateListView
from orders.models import Order, OrderItem
from services.models import Service, Item, Price # Added Service, Item
# from django import forms # Not used directly in views.py if forms are in forms.py
from .forms import RegistrationForm, ProfessionalChoiceForm, DepositPaymentForm
from labels.models import Label


# --- Mixins ---
class CustomerRequiredMixin(UserPassesTestMixin):
    """Ensures the logged-in user has a customer profile."""
    def test_func(self):
        try:
            return hasattr(self.request.user, 'customer_profile') and self.request.user.customer_profile is not None
        except AttributeError: # For AnonymousUser
            return False

    def handle_no_permission(self):
        messages.error(self.request, "You need a customer profile to access this page.")
        if not self.request.user.is_authenticated:
            return redirect('login') # Or your specific login URL
        # If authenticated but no customer profile, redirect to a relevant page
        # For example, a profile choice or creation page if you have one.
        return redirect('users:user_management') # Or a more suitable page

class AgentRequiredMixin(UserPassesTestMixin):
    """Ensures the logged-in user has an agent profile."""
    def test_func(self):
        try:
            return hasattr(self.request.user, 'agent_profile') and self.request.user.agent_profile is not None
        except AttributeError: # For AnonymousUser
            return False

    def handle_no_permission(self):
        messages.error(self.request, "You need an agent profile to access this page.")
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('users:user_management') # Or a more suitable page

# --- Class-Based Views ---

class UserRegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:user_management')

    def form_valid(self, form):
        print("FORM VALID", form.cleaned_data)
        email = form.cleaned_data['email']
        
        # Check for existing email first
        if User.objects.filter(email=email).exists():
            login_url = reverse('login')
            error_message = mark_safe(
                f'Email address {escape(email)} already exists, please <a href="{escape(login_url)}">login instead</a>'
            )
            messages.error(self.request, error_message)
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                # Create user first
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    password=form.cleaned_data['password']
                )
                print(f"Created user: {user.email} ID: {user.id}")

                # Create corresponding profile
                if form.cleaned_data['role'] == 'customer':
                    Customer.objects.create(
                        user=user,
                        wedding_day=form.cleaned_data.get('wedding_day')
                    )
                    print("Created customer profile")
                elif form.cleaned_data['role'] == 'professional': # Make this explicit
                    prof = Professional.objects.create(
                        user=user,
                        title=form.cleaned_data['title']
                    )
                    print("Created professional profile:", prof.title)
                elif form.cleaned_data['role'] == 'agent': # New role
                    Agent.objects.create(user=user)
                    print("Created agent profile")

                # Log in user directly
                login(self.request, user)
                messages.success(self.request, 'Registration successful. You are now logged in.')

                if form.cleaned_data['role'] == 'customer':
                    # New redirect for customers
                    return redirect(reverse_lazy('users:deposit_payment'))
                else:
                    # Professionals and Agents redirect to user_management
                    return redirect(self.success_url)

        except Exception as e:
            print(f"EXCEPTION DURING REGISTRATION: {repr(e)}")
            if 'user' in locals():
                print("Cleaning up - deleting created user")
                user.delete()
            messages.error(self.request, "An unexpected error occurred during registration. Please try again.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("FORM INVALID", form.errors)
        return super().form_invalid(form)

class UserManagementView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            customer = user.customer_profile
        except Customer.DoesNotExist: # User is not a customer (could be Professional or Admin without CustomerProfile)
            # Professionals or other non-customer users see a generic management page.
            return render(request, 'users/management.html', {'page_title': "User Management"})

        # User is a customer, check for active ProfessionalCustomerLink
        link = ProfessionalCustomerLink.objects.filter(
            customer=customer,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        ).select_related('professional__user').first() # Added professional__user to select_related

        if link:
            # Customer is linked to a professional, show customer dashboard
            return render(request, 'users/customer_dashboard.html', {
                'professional': link.professional,
                'page_title': "My Dashboard"
            })
        else:
            # Customer not linked, show professional selection form
            form = ProfessionalChoiceForm()
            return render(request, 'users/customer_choose_professional.html', {
                'form': form,
                'page_title': "Choose Your Professional"
            })

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            customer = user.customer_profile
        except Customer.DoesNotExist:
            messages.error(request, "Only customers can link to a professional.")
            return redirect('home') # Or some other appropriate redirect

        form = ProfessionalChoiceForm(request.POST)
        if form.is_valid():
            professional = form.cleaned_data['professional']
            try:
                with transaction.atomic():
                    # Ensure no other active link exists before creating a new one.
                    # This could happen if user navigates away and back.
                    ProfessionalCustomerLink.objects.filter(
                        customer=customer,
                        status=ProfessionalCustomerLink.StatusChoices.ACTIVE
                    ).delete() # Or set to INACTIVE if history is important

                    ProfessionalCustomerLink.objects.create(
                        professional=professional,
                        customer=customer,
                        status=ProfessionalCustomerLink.StatusChoices.ACTIVE
                    )
                messages.success(request, f"You are now linked with {professional.title or professional.user.get_full_name()}.")
                # Redirect to a relevant page, e.g., where they can start selecting items/services
                # Assuming 'orders:select_items' requires an order_pk.
                # This flow might need adjustment depending on when an order is created.
                # For now, redirecting to user_management which should show the dashboard.
                return redirect('users:user_management')
            except Exception as e:
                # Log error e
                print("EXCEPTION DURING REGISTRATION:", e)
                messages.error(self.request, "An unexpected error occurred during registration. Please try again.")
                return self.form_invalid(form)
                
        # Form is invalid or an error occurred, re-render the choice form
        return render(request, 'users/customer_choose_professional.html', {
            'form': form,
            'page_title': "Choose Your Professional"
        })


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "My Profile"
        # The user object (request.user) is automatically available in templates.
        # Explicitly pass profiles if needed for clarity or specific access patterns.
        if hasattr(self.request.user, 'customer_profile'):
            context['customer_profile'] = self.request.user.customer_profile
        if hasattr(self.request.user, 'professional_profile'):
            context['professional_profile'] = self.request.user.professional_profile
        return context


class ChangeProfessionalView(LoginRequiredMixin, CustomerRequiredMixin, FormView):
    form_class = ProfessionalChoiceForm
    template_name = 'users/customer_choose_professional.html' # Reuses the same template
    success_url = reverse_lazy('users:user_management')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Change Your Professional"
        context['form_title'] = "Select a New Professional" # Custom title for this context
        return context

    def form_valid(self, form):
        customer = self.request.user.customer_profile # CustomerRequiredMixin ensures this exists
        new_professional = form.cleaned_data['professional']

        try:
            with transaction.atomic():
                # Deactivate or delete existing active links
                ProfessionalCustomerLink.objects.filter(
                    customer=customer,
                    status=ProfessionalCustomerLink.StatusChoices.ACTIVE
                ).delete() # Or update to INACTIVE if history is important

                # Create the new link
                ProfessionalCustomerLink.objects.create(
                    professional=new_professional,
                    customer=customer,
                    status=ProfessionalCustomerLink.StatusChoices.ACTIVE
                )
            messages.success(self.request, f"You have successfully changed your professional to {new_professional.title or new_professional.user.get_full_name()}.")
        except Exception as e:
            # Log error e
            messages.error(self.request, "An error occurred while changing your professional. Please try again.")
            # Redirect back to the form or a relevant error page
            return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())



class CustomerTemplateListView(LoginRequiredMixin, CustomerRequiredMixin, ListView):
    model = Template
    template_name = 'users/customer_template_list.html'
    context_object_name = 'templates'

    def get_queryset(self):
        customer = self.request.user.customer_profile
        try:
            # Find the active professional linked to this customer
            active_link = ProfessionalCustomerLink.objects.get(
                customer=customer,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            )
            linked_professional = active_link.professional
            # Return templates from that professional, prefetching images for efficiency
            return Template.objects.filter(professional=linked_professional).prefetch_related('images')
        except ProfessionalCustomerLink.DoesNotExist:
            # If no active link is found, the customer isn't properly set up or has no professional.
            # Inform the user and return no templates.
            messages.warning(self.request, "You are not currently linked with any professional. Please choose one to see their templates.")
            return Template.objects.none()
        except Exception as e:
            # Handle other potential errors, e.g., database issues
            messages.error(self.request, "An error occurred while retrieving templates.")
            # Log the error e for admin review
            print(f"Error in CustomerTemplateListView get_queryset: {e}")
            return Template.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Templates from your Professional"
        # Add the linked professional to the context if they exist, for display purposes
        try:
            customer = self.request.user.customer_profile
            active_link = ProfessionalCustomerLink.objects.get(
                customer=customer,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            )
            context['linked_professional'] = active_link.professional
        except ProfessionalCustomerLink.DoesNotExist:
            context['linked_professional'] = None

        # Prepare data for Vue.js
        templates_qs = context.get('templates', Template.objects.none()) # Get templates from context or empty queryset

        templates_list_for_json = []
        placeholder_image_url = static('core/images/placeholder.png') # Define placeholder once

        for template_item in templates_qs:
            default_image_url = placeholder_image_url
            # .images is the related manager from Template to TemplateImage
            # We prefetched 'images' in get_queryset
            default_image = None
            for img in template_item.images.all(): # Iterate over prefetched images
                if img.is_default:
                    default_image = img
                    break

            if default_image and hasattr(default_image.image, 'url'):
                default_image_url = default_image.image.url

            description_snippet = template_item.description
            if description_snippet and len(description_snippet) > 100:
                description_snippet = description_snippet[:97] + "..."
            elif not description_snippet:
                description_snippet = "" # Ensure it's a string

            templates_list_for_json.append({
                'pk': template_item.pk,
                'title': template_item.title,
                'description_snippet': description_snippet,
                'default_image_url': default_image_url,
            })

        context['templates_json'] = json.dumps(templates_list_for_json)

        return context


class CustomerTemplateDetailView(LoginRequiredMixin, CustomerRequiredMixin, UserPassesTestMixin, DetailView):
    model = Template
    template_name = 'users/customer_template_detail.html' # To be created
    context_object_name = 'template'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        """
        Initial queryset filtering: ensures the template belongs to *a* professional
        and prefetches related data. The actual check for *this customer's*
        professional is done in test_func.
        """
        # This queryset is further filtered by UserPassesTestMixin or implicitly by DetailView's get_object
        # to ensure the object exists before test_func is called with self.get_object().
        # We ensure the template is active or visible if such flags exist.
        # For now, just prefetching. The professional link check is vital.

        # Get the customer and their linked professional
        try:
            customer = self.request.user.customer_profile
            active_link = ProfessionalCustomerLink.objects.get(
                customer=customer,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            )
            linked_professional = active_link.professional
            # Return templates from that professional, prefetching images and services details
            return Template.objects.filter(professional=linked_professional).prefetch_related(
                'images',
                'services__category', # For displaying service category
                'services__items__prices' # For "Update Basket" logic later
            )
        except ProfessionalCustomerLink.DoesNotExist:
            # If no active link, this customer should not see any templates.
            # The CustomerRequiredMixin and LoginRequiredMixin should ideally prevent this,
            # but as a safeguard:
            return Template.objects.none()
        except AttributeError: # request.user.customer_profile might not exist if mixin order is wrong or user is anon
             return Template.objects.none()


    def test_func(self):
        """
        Ensures the logged-in customer is linked to the professional who owns this template.
        """
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'customer_profile'):
            return False # Should be caught by LoginRequiredMixin & CustomerRequiredMixin

        template = self.get_object() # Gets the template based on pk from URL and get_queryset

        try:
            customer = self.request.user.customer_profile
            active_link = ProfessionalCustomerLink.objects.select_related('professional').get(
                customer=customer,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            )
            linked_professional = active_link.professional

            # The crucial check: Does this template belong to the customer's linked professional?
            if template.professional == linked_professional:
                return True
        except ProfessionalCustomerLink.DoesNotExist:
            # Customer is not linked to any professional.
            messages.error(self.request, "You are not linked to a professional, so you cannot view this template.")
            return False
        except Exception as e:
            # Log e for debugging
            messages.error(self.request, "An unexpected error occurred.")
            return False

        messages.error(self.request, "You are not authorized to view this template.")
        return False

    def handle_no_permission(self):
        # This method is called if test_func returns False
        # Redirect to a safe page, like the template list or user management
        # messages.error(self.request, "You do not have permission to view this template.") already set in test_func
        # Check if there's a linked professional to decide the redirect
        try:
            customer = self.request.user.customer_profile
            ProfessionalCustomerLink.objects.get(customer=customer, status=ProfessionalCustomerLink.StatusChoices.ACTIVE)
            # If linked, they tried to access a wrong template, so template list is fine
            return redirect('users:customer_template_list')
        except ProfessionalCustomerLink.DoesNotExist:
            # If not linked at all, guide them to management to choose one
            return redirect('users:user_management')
        except AttributeError: # E.g. AnonymousUser
            return redirect('login')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = self.object # self.object is the template instance

        context['page_title'] = template.title

        default_image = None
        other_images = []
        # Iterate over prefetched images
        for img in template.images.all():
            if img.is_default:
                default_image = img
            else:
                other_images.append(img)

        context['default_image'] = default_image
        context['other_images'] = other_images

        # For clarity in template, pass services directly if needed, though template.services.all will work
        # context['services_in_template'] = template.services.all() # Already prefetched

        # The linked professional might be useful for display
        try:
            customer = self.request.user.customer_profile
            active_link = ProfessionalCustomerLink.objects.select_related('professional__user').get(
                customer=customer,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            )
            context['linked_professional'] = active_link.professional
        except ProfessionalCustomerLink.DoesNotExist:
            context['linked_professional'] = None
            # This case should ideally be handled by test_func or earlier redirects

        return context


    @transaction.atomic
    def post(self, request, *args, **kwargs):
        template = self.get_object() # Template instance
        customer = request.user.customer_profile # Customer profile

        if not template.services.exists():
            messages.warning(request, "This template has no services to add to the basket.")
            return redirect(request.path_info)

        # Determine the currency for the order
        order_currency = 'EUR' # Default
        if hasattr(customer, 'preferred_currency') and customer.preferred_currency:
            order_currency = customer.preferred_currency
        elif template.professional and hasattr(template.professional, 'default_currency') and template.professional.default_currency:
            order_currency = template.professional.default_currency

        # Handle order retrieval/creation
        pending_orders = Order.objects.filter(
            customer=customer,
            status=Order.StatusChoices.PENDING
        ).order_by('-updated_at') # Get the most recently updated

        order = None
        created_order_for_template = False # Flag if we created/repurposed an order specifically for this template

        if pending_orders.exists():
            if pending_orders.count() > 1:
                messages.warning(
                    request,
                    "Multiple pending orders found. Using the most recently updated one. "
                    "Please review and consolidate your pending orders."
                )
            order = pending_orders.first()
        else:
            order = Order.objects.create(
                customer=customer,
                status=Order.StatusChoices.PENDING,
                currency=order_currency
            )
            created_order_for_template = True

        # Check currency and professional context if using an existing order
        if not created_order_for_template:
            if order.currency != order_currency:
                if order.items.exists():
                    # Infer professional context from existing items
                    existing_items_professional = None
                    first_item_in_order = order.items.first()
                    if first_item_in_order and hasattr(first_item_in_order, 'professional') and first_item_in_order.professional:
                        existing_items_professional = first_item_in_order.professional

                    if existing_items_professional and existing_items_professional != template.professional:
                        messages.error(
                            request,
                            f"Your current pending order (in {order.currency}) has items from {existing_items_professional.title}. "
                            f"This template is from {template.professional.title}. "
                            f"Mixing items from different professionals in one order is not currently supported this way. "
                            f"Please finalize or clear your current pending order, or create a new one."
                        )
                        return redirect('orders:order_detail', pk=order.pk)
                    else: # Items exist, currency differs, but professional context seems compatible or undetermined
                         messages.error(
                            request,
                            f"Your existing pending order (in {order.currency}) contains items. "
                            f"Items from this template would be added in {order_currency}. "
                            f"Please resolve the currency difference or ensure the order is empty to change its currency."
                        )
                         return redirect('orders:order_detail', pk=order.pk)
                else:
                    # Order is empty, safe to update its currency
                    order.currency = order_currency
                    order.save()
                    messages.info(request, f"Updated currency of your empty pending order to {order_currency}.")

        # Add items from template to the order
        items_added_count = 0
        for service_from_template in template.services.all().prefetch_related('items__prices'):
            for item_from_template in service_from_template.items.all():
                # Prioritize price in order's currency, then any active price
                current_price = item_from_template.prices.filter(is_active=True, currency=order.currency).first()
                if not current_price:
                    current_price = item_from_template.prices.filter(is_active=True).first()

                if current_price:
                    OrderItem.objects.create(
                        order=order,
                        professional=template.professional, # Professional from the template
                        service=service_from_template,
                        item=item_from_template,
                        price=current_price, # Assign the Price object here
                        quantity=1, # Default quantity for template items
                        price_amount_at_order=current_price.amount,
                        price_currency_at_order=current_price.currency, # Actual currency of the price used
                        price_frequency_at_order=current_price.frequency
                    )
                    items_added_count += 1
                else:
                    messages.warning(request, f"Item '{item_from_template.title}' from service '{service_from_template.title}' could not be added as no active price was found.")

        if items_added_count > 0:
            if hasattr(order, 'calculate_total_and_save'): # Ideal method
                order.calculate_total_and_save()
            elif hasattr(order, 'calculate_total'): # Common pattern
                order.calculate_total()
                order.save()
            else: # Fallback, just save
                order.save()
            messages.success(request, f"{items_added_count} item(s) from template '{template.title}' have been added to your basket.")
        else:
            # Only show this generic message if no specific warnings (like "no services" or "no active price") were added.
            # This check might be tricky if messages were added then cleared, or if multiple messages are okay.
            # For simplicity, we'll show it if no items were added, relying on earlier specific messages for details.
            if not messages.get_messages(request): # A simple check
                 messages.info(request, "No items were added to your basket. This might be due to missing prices or other issues.")


        return redirect('orders:order_detail', pk=order.pk) # Corrected kwarg to 'pk'


class DepositPaymentView(LoginRequiredMixin, CustomerRequiredMixin, FormView):
    template_name = 'users/deposit_payment.html'
    form_class = DepositPaymentForm
    success_url = reverse_lazy('users:user_management')

    def form_valid(self, form):
        customer_profile = self.request.user.customer_profile
        try:
            # Corrected label_type to 'CUSTOMER' as per previous migration correction
            deposit_label = Label.objects.get(name='deposit_paid', label_type='CUSTOMER')
            customer_profile.labels.add(deposit_label)
            # customer_profile.save() # Not typically needed for M2M add, but as a test? No, let's not add this yet.
            messages.success(self.request, "Thank you for confirming your deposit payment. Your account is now fully active.")
            return super().form_valid(form)
        except Label.DoesNotExist:
            messages.error(self.request, "Critical error: The 'deposit_paid' label is not configured. Please contact support.")
            return self.form_invalid(form)
        except Exception as e:
            # Add a message for any other exception to make it visible in tests if it leads to form_invalid
            messages.error(self.request, f"An unexpected error occurred: {e}")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Deposit Payment"
        return context


class AgentSelectProfessionalView(LoginRequiredMixin, AgentRequiredMixin, ListView):
    model = Professional
    template_name = 'users/agent_select_professional.html' # New template
    context_object_name = 'professionals'

    def get_queryset(self):
        # Return active professionals, or any other filtering needed
        return Professional.objects.all().select_related('user') # Example: get all

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Select a Professional"
        return context


class AgentCreateOrderView(LoginRequiredMixin, AgentRequiredMixin, View):
    template_name = 'users/agent_create_order.html'

    def get(self, request, professional_id):
        professional = get_object_or_404(Professional, pk=professional_id)
        services_with_items = []
        # Attempt to get agent's preferred currency, default to EUR
        agent_preferred_currency = 'EUR' # Default
        if request.user.agent_profile and hasattr(request.user.agent_profile, 'preferred_currency') and request.user.agent_profile.preferred_currency:
            agent_preferred_currency = request.user.agent_profile.preferred_currency
        elif hasattr(request.user.agent_profile.user, 'customer_profile') and request.user.agent_profile.user.customer_profile.preferred_currency: # Fallback to linked customer profile currency
            agent_preferred_currency = request.user.agent_profile.user.customer_profile.preferred_currency


        for service in Service.objects.filter(professional=professional, is_active=True).prefetch_related('items__prices'):
            items = []
            for item in service.items.filter(is_active=True):
                active_price = item.prices.filter(is_active=True, currency=agent_preferred_currency).first()
                if not active_price:
                    active_price = item.prices.filter(is_active=True, currency='EUR').first() # Fallback to EUR
                if not active_price:
                    active_price = item.prices.filter(is_active=True).first() # Fallback to any active price

                if active_price:
                    items.append({'item': item, 'active_price': active_price})
            if items:
                services_with_items.append({'service': service, 'items_with_prices': items})

        context = {
            'professional': professional,
            'services_with_items': services_with_items,
            'page_title': f"Create Order for {professional.title or professional.user.get_full_name()}"
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, professional_id):
        agent_profile = request.user.agent_profile
        professional = get_object_or_404(Professional, pk=professional_id)
        item_id = request.POST.get('item_id')
        quantity_str = request.POST.get('quantity', '1')

        if not item_id:
            messages.error(request, "No item selected.")
            return redirect(request.path_info)

        try:
            item = Item.objects.select_related('service').get(pk=item_id)
            if item.service.professional != professional:
                messages.error(request, "Invalid item for this professional.")
                return redirect(request.path_info)

            quantity = int(quantity_str)
            if quantity <= 0:
                messages.error(request, "Quantity must be positive.")
                return redirect(request.path_info)

        except (Item.DoesNotExist, ValueError):
            messages.error(request, "Invalid item or quantity.")
            return redirect(request.path_info)

        order_currency = getattr(agent_profile, 'preferred_currency', 'EUR')
        if hasattr(request.user.agent_profile.user, 'customer_profile') and request.user.agent_profile.user.customer_profile.preferred_currency: # Fallback to linked customer profile currency
            order_currency = request.user.agent_profile.user.customer_profile.preferred_currency


        order, created = Order.objects.get_or_create(
            agent=agent_profile,
            # professional_id=professional.pk, # This would be if Order has direct FK to Professional
            status=Order.StatusChoices.PENDING,
            defaults={'currency': order_currency}
        )

        if not created and order.currency != order_currency:
            # This logic might need refinement: what if agent wants to change currency for an empty pending order?
            # For now, use existing order's currency.
            messages.warning(request, f"An existing pending order was found with currency {order.currency}. New items will use this currency.")
            order_currency = order.currency # Ensure consistency

        active_price = item.prices.filter(is_active=True, currency=order_currency).first()
        if not active_price: # Fallback to EUR if specific currency not found
             active_price = item.prices.filter(is_active=True, currency='EUR').first()
        if not active_price: # Fallback to any active price if EUR also not found
            active_price = item.prices.filter(is_active=True).first()

        if not active_price:
            messages.error(request, f"No active price found for item '{item.title}' in a compatible currency.")
            return redirect(request.path_info)

        order_item, item_created = OrderItem.objects.get_or_create(
            order=order,
            item=item,
            professional=professional, # Explicitly set professional for this OrderItem
            service=item.service,     # Explicitly set service for this OrderItem
            defaults={
                'price': active_price,
                'quantity': quantity,
                'price_amount_at_order': active_price.amount,
                'price_currency_at_order': active_price.currency,
                'price_frequency_at_order': active_price.frequency,
            }
        )

        if not item_created:
            order_item.quantity += quantity
            order_item.save(update_fields=['quantity']) # Be specific about updated fields
            messages.success(request, f"Updated quantity of '{item.title}' in your basket.")
        else:
            messages.success(request, f"Added '{item.title}' to your basket.")

        order.calculate_total()

        return redirect(request.path_info)


class AgentOrderListView(LoginRequiredMixin, AgentRequiredMixin, TemplateView):
    template_name = 'users/agent_order_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "My Orders"
        # Pass the API endpoint URL to the template for Vue
        context['orders_api_url'] = reverse('orders:agent_orders_api')
        return context
