from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.models import Customer
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from .models import Order, OrderItem
from users.models import Customer, Professional, ProfessionalCustomerLink 

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
        # CHANGED: Fixed URL name from 'profile_choice' to 'user_management'
        return redirect('users:user_management') # Or 'users:customer_profile_create'
    
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

        # Support agent viewing their assigned orders
        if hasattr(self.request.user, 'agent_profile') and self.request.user.agent_profile:
            if self.order.assigned_agent == self.request.user.agent_profile:
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
            if hasattr(self.request.user, 'agent_profile') and self.request.user.agent_profile:  # Support agent redirect
                return redirect('users:agent_management')
            elif hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile:
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
    4. User is an Agent assigned to this order AND order is PENDING.  # Support agent-created orders
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
            
        # Support agent-created orders (no customer) - agent assigned to this order
        if hasattr(self.request.user, 'agent_profile') and self.request.user.agent_profile:
            if self.order.assigned_agent == self.request.user.agent_profile and self.order.status == Order.StatusChoices.PENDING:
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

