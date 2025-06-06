from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView, View
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Prefetch
from django.http import HttpResponseRedirect

from .models import Professional, Customer, ProfessionalCustomerLink
from orders.models import Order, OrderItem
from labels.models import Label
from .forms import CustomerLabelForm

class ProfessionalRequiredMixin(UserPassesTestMixin):
    """Ensures the logged-in user has a professional profile."""
    def test_func(self):
        try:
            return hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None
        except AttributeError:  # For AnonymousUser
            return False

    def handle_no_permission(self):
        messages.error(self.request, "You need a professional profile to access this page.")
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('users:user_management')


class CustomerManagementView(LoginRequiredMixin, ProfessionalRequiredMixin, ListView):
    """View for professionals to manage their linked customers."""
    model = ProfessionalCustomerLink
    template_name = 'users/customer_management.html'
    context_object_name = 'customer_links'
    
    def get_queryset(self):
        professional = self.request.user.professional_profile
        return ProfessionalCustomerLink.objects.filter(
            professional=professional,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        ).select_related('customer__user').order_by('customer__user__last_name', 'customer__user__first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Customer Management"
        return context


class CustomerDetailView(LoginRequiredMixin, ProfessionalRequiredMixin, DetailView):
    """View for professionals to see details of a specific customer."""
    model = Customer
    template_name = 'users/customer_detail.html'
    context_object_name = 'customer'
    pk_url_kwarg = 'customer_id'
    
    def get_queryset(self):
        professional = self.request.user.professional_profile
        # Only allow viewing customers linked to this professional
        return Customer.objects.filter(
            professional_links__professional=professional,
            professional_links__status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        ).prefetch_related('labels')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.object
        
        # Get customer's orders
        orders = Order.objects.filter(customer=customer).order_by('-order_date')
        
        # Get current basket (pending order)
        basket = orders.filter(status=Order.StatusChoices.PENDING).first()
        
        context.update({
            'page_title': f"Customer: {customer.user.get_full_name() or customer.user.username}",
            'orders': orders,
            'basket': basket,
            'label_form': CustomerLabelForm(instance=customer)
        })
        return context


class CustomerBasketView(LoginRequiredMixin, ProfessionalRequiredMixin, DetailView):
    """View for professionals to see and edit a customer's basket."""
    model = Order
    template_name = 'users/customer_basket.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def get_queryset(self):
        professional = self.request.user.professional_profile
        # Only allow viewing baskets of customers linked to this professional
        return Order.objects.filter(
            customer__professional_links__professional=professional,
            customer__professional_links__status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        ).prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related(
                    'price__item__service',
                    'price__item',
                    'price'
                ).order_by('price__item__service__title', 'price__item__title')
            )
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Customer Basket: {self.object.customer.user.get_full_name() or self.object.customer.user.username}"
        return context


class CustomerLabelUpdateView(LoginRequiredMixin, ProfessionalRequiredMixin, UpdateView):
    """View for professionals to update a customer's labels."""
    model = Customer
    form_class = CustomerLabelForm
    template_name = 'users/customer_label_form.html'
    pk_url_kwarg = 'customer_id'
    
    def get_queryset(self):
        professional = self.request.user.professional_profile
        # Only allow updating labels of customers linked to this professional
        return Customer.objects.filter(
            professional_links__professional=professional,
            professional_links__status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )
    
    def get_success_url(self):
        return reverse('users:customer_detail', kwargs={'customer_id': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f"Labels updated for {self.object.user.get_full_name() or self.object.user.username}")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Update Labels: {self.object.user.get_full_name() or self.object.user.username}"
        return context

