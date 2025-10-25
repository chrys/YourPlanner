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
from decimal import Decimal
from .models import Professional, Customer, ProfessionalCustomerLink
from packages.models import Template, TemplateImage # For CustomerTemplateListView
from orders.models import Order, OrderItem
from services.models import Price, Service # Needed for finding active price for an item
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


# --- Class-Based Views ---

class CustomerProfessionalServicesView(LoginRequiredMixin, CustomerRequiredMixin, ListView):
    model = Service
    template_name = 'users/customer_professional_services.html'
    context_object_name = 'services'

    def get_queryset(self):
        # Ensure customer_profile exists due to CustomerRequiredMixin
        customer = self.request.user.customer_profile
        try:
            # Get the active professional link for the customer
            active_link = ProfessionalCustomerLink.objects.select_related('professional__user').get(
                customer=customer,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE # Make sure this status choice exists
            )
            self.linked_professional = active_link.professional
            # Fetch active services from the linked professional
            return Service.objects.filter(
                professional=self.linked_professional,
                is_active=True,
                professional__user__is_active=True # Also ensure the professional's user account is active
            ).order_by('title')
        except ProfessionalCustomerLink.DoesNotExist:
            self.linked_professional = None
            messages.warning(self.request, "You are not currently linked with an active professional. Please choose one from your management page.")
            return Service.objects.none()
        except Exception as e:
            # Log the error e for admin review
            self.linked_professional = None
            messages.error(self.request, "An error occurred while trying to retrieve services. Please try again later.")
            return Service.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Services from Your Professional"
        if hasattr(self, 'linked_professional') and self.linked_professional:
            prof_display_name = self.linked_professional.title or \
                                self.linked_professional.user.get_full_name() or \
                                self.linked_professional.user.username
            context['page_title'] = f"Services from {prof_display_name}"
            context['linked_professional'] = self.linked_professional
        else:
            # This case should ideally be handled by the queryset returning none
            # and a message being displayed.
            context['linked_professional'] = None
        return context


class UserRegistrationView(CreateView):
    template_name = 'users/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('users:user_management')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_default_professional'] = Professional.objects.filter(default=True).exists()
        return context

    def form_valid(self, form):
        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            login_url = reverse('login')
            error_message = mark_safe(
                f'Email address {escape(email)} already exists, please <a href="{escape(login_url)}">login instead</a>'
            )
            messages.error(self.request, error_message)
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    password=form.cleaned_data['password']
                )

                # If there's a default professional, always create customer
                if Professional.objects.filter(default=True).exists():
                    customer = Customer.objects.create(
                        user=user,
                        wedding_day=form.cleaned_data['wedding_day']
                    )
                    # Automatically link to default professional
                    default_professional = Professional.objects.get(default=True)
                    ProfessionalCustomerLink.objects.create(
                        professional=default_professional,
                        customer=customer,
                        status=ProfessionalCustomerLink.StatusChoices.ACTIVE
                    )
                    messages.success(self.request, f'Registration successful. You are now linked with {default_professional.title}.')
                else:
                    # Original logic for when no default professional exists
                    if form.cleaned_data['role'] == 'customer':
                        Customer.objects.create(
                            user=user,
                            wedding_day=form.cleaned_data['wedding_day']
                        )
                    else:
                        Professional.objects.create(
                            user=user,
                            title=form.cleaned_data['title']
                        )

                login(self.request, user)
                if form.cleaned_data['role'] == 'customer':
                    return redirect(reverse_lazy('users:deposit_payment'))
                return redirect(self.success_url)

        except Exception as e:
            if 'user' in locals():
                user.delete()
            messages.error(self.request, "An unexpected error occurred during registration. Please try again.")
            return self.form_invalid(form)
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
        template = self.get_object() # CHANGE: Get template object
        customer = request.user.customer_profile

        if not template.services.exists():
            messages.warning(request, "This template has no services to add to the basket.")
            return redirect(request.path_info)

        # CHANGE: Parse guest count from form
        try:
            guest_count_raw = request.POST.get('guest_count')
            guest_count = int(guest_count_raw) if guest_count_raw is not None else template.default_guests
        except (ValueError, TypeError):
            guest_count = template.default_guests

        # CHANGE: Compute template total price
        additional_guests = max(0, guest_count - (template.default_guests or 0))
        template_total = (template.base_price or Decimal('0.00')) + (template.price_per_additional_guest or Decimal('0.00')) * Decimal(additional_guests)

        # CHANGE: Fetch or create pending order
        pending_orders = Order.objects.filter(
            customer=customer,
            status=Order.StatusChoices.PENDING
        ).order_by('-updated_at')

        order = None
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
                currency=template.currency  # CHANGE: Set currency from template
            )

        # CHANGE: Set template snapshot on order (do NOT create OrderItem rows)
        order.template = template
        order.template_guest_count = guest_count
        order.template_total_amount = template_total
        order.total_amount = template_total  # CHANGE: Start with template price
        order.currency = template.currency  # CHANGE: Enforce template currency
        order.save()

        messages.success(
            request,
            f"Package '{template.title}' added to your basket. "
            f"Price: {template_total} {template.currency} for {guest_count} guest(s)."
        )
        return redirect('orders:order_detail', pk=order.pk)

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
