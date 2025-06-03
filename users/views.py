from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.safestring import mark_safe
# from django.core.exceptions import ValidationError # Not used
from django.db import transaction
# from django.utils.html import escape # Not used
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, View, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Professional, Customer, ProfessionalCustomerLink
# from orders.models import Order, OrderItem # Not used in these views directly
# from django import forms # Not used directly in views.py if forms are in forms.py
from .forms import RegistrationForm, ProfessionalChoiceForm


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

class UserRegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:user_management')  # Changed from 'login' to 'users:user_management'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            login_url = reverse('login')
            error_html = mark_safe(
                f'This email is already registered. Please <a href="{escape(login_url)}">log in instead</a>.'
            )
            # form.add_error('email', error_html) # This way might render escaped HTML in form
            messages.error(self.request, error_html) # Use messages framework for this kind of error
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email, # Using email as username
                    email=email,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    password=form.cleaned_data['password'],
                )
                role = form.cleaned_data['role']
                if role == 'customer':
                    Customer.objects.create(user=user)
                else: # Professional
                    Professional.objects.create(
                        user=user,
                        title=form.cleaned_data['title']
                    )
            messages.success(self.request, 'Registration successful.')
            # Automatically log in the user after registration
            from django.contrib.auth import login
            from django.contrib.auth import authenticate
            user = authenticate(username=email, password=form.cleaned_data['password'])
            if user is not None:
                login(self.request, user)
                return HttpResponseRedirect(self.get_success_url())
            else:
                return HttpResponseRedirect(reverse_lazy('login'))
        except Exception as e: # Catch any other unexpected error during transaction
            # Log the error e
            messages.error(self.request, "An unexpected error occurred during registration. Please try again.")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Register" # Example of adding more context
        return context


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
                messages.error(request, "An error occurred while linking with the professional. Please try again.")

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
