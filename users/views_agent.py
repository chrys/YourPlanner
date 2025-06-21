from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect

from .models import Agent, Professional
from .forms import AgentSelectProfessionalForm, AgentOrderForm
from orders.models import Order, OrderItem
from services.models import Service, Item, Price

class AgentRequiredMixin(LoginRequiredMixin):
    """Mixin that verifies the user is an agent."""
    def dispatch(self, request, *args, **kwargs):
        try:
            self.agent = request.user.agent_profile
        except Agent.DoesNotExist:
            messages.error(request, "You must be an agent to access this page.")
            return redirect('users:user_management')
        return super().dispatch(request, *args, **kwargs)

class AgentCreateOrderView(AgentRequiredMixin, FormView):
    """View for agents to select a professional for a new order."""
    template_name = 'users/agent_select_professional.html'
    form_class = AgentSelectProfessionalForm
    
    def form_valid(self, form):
        professional = form.cleaned_data['professional']
        # Store the professional ID in session for the next step
        self.request.session['selected_professional_id'] = professional.pk
        return redirect('users:agent_select_services')

class AgentSelectServicesView(AgentRequiredMixin, View):
    """View for agents to select services and items from the chosen professional."""
    
    def get(self, request, *args, **kwargs):
        # Get the professional from session
        professional_id = request.session.get('selected_professional_id')
        if not professional_id:
            messages.error(request, "Please select a professional first.")
            return redirect('users:agent_create_order')
        
        professional = get_object_or_404(Professional, pk=professional_id)
        services = Service.objects.filter(professional=professional, is_active=True)
        
        return render(request, 'users/agent_select_services.html', {
            'professional': professional,
            'services': services,
            'page_title': "Select Services and Items"
        })
    
    def post(self, request, *args, **kwargs):
        # Get the professional from session
        professional_id = request.session.get('selected_professional_id')
        if not professional_id:
            messages.error(request, "Please select a professional first.")
            return redirect('users:agent_create_order')
        
        professional = get_object_or_404(Professional, pk=professional_id)
        
        # Get selected items and quantities from the form
        selected_items = {}
        for key, value in request.POST.items():
            if key.startswith('item_') and value and int(value) > 0:
                item_id = key.replace('item_', '')
                selected_items[item_id] = int(value)
        
        if not selected_items:
            messages.error(request, "Please select at least one item.")
            return self.get(request, *args, **kwargs)
        
        # Store selected items in session for the next step
        request.session['selected_items'] = selected_items
        return redirect('users:agent_finalize_order')

class AgentFinalizeOrderView(AgentRequiredMixin, FormView):
    """View for agents to finalize the order details."""
    template_name = 'users/agent_finalize_order.html'
    form_class = AgentOrderForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the professional and selected items from session
        professional_id = self.request.session.get('selected_professional_id')
        selected_items = self.request.session.get('selected_items', {})
        
        if not professional_id or not selected_items:
            messages.error(self.request, "Please start the order process again.")
            return redirect('users:agent_create_order')
        
        professional = get_object_or_404(Professional, pk=professional_id)
        
        # Get the items and their details
        items_details = []
        total_amount = 0
        
        for item_id, quantity in selected_items.items():
            item = get_object_or_404(Item, pk=item_id)
            # Get the active price for this item
            price = Price.objects.filter(item=item, is_active=True).first()
            
            if price:
                subtotal = price.amount * quantity
                total_amount += subtotal
                
                items_details.append({
                    'item': item,
                    'price': price,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
        
        context.update({
            'professional': professional,
            'items_details': items_details,
            'total_amount': total_amount,
            'page_title': "Finalize Order"
        })
        
        return context
    
    def form_valid(self, form):
        # Get the agent, professional, and selected items
        agent = self.request.user.agent_profile
        professional_id = self.request.session.get('selected_professional_id')
        selected_items = self.request.session.get('selected_items', {})
        
        if not professional_id or not selected_items:
            messages.error(self.request, "Please start the order process again.")
            return redirect('users:agent_create_order')
        
        professional = get_object_or_404(Professional, pk=professional_id)
        
        try:
            with transaction.atomic():
                # Create the order
                order = Order.objects.create(
                    agent=agent,
                    order_date=form.cleaned_data.get('order_date', None),
                    notes=form.cleaned_data.get('notes', ''),
                    currency=form.cleaned_data.get('currency', 'EUR')
                )
                
                # Add the items to the order
                position = 0
                for item_id, quantity in selected_items.items():
                    item = get_object_or_404(Item, pk=item_id)
                    service = item.service
                    # Get the active price for this item
                    price = Price.objects.filter(item=item, is_active=True).first()
                    
                    if price:
                        OrderItem.objects.create(
                            order=order,
                            professional=professional,
                            service=service,
                            item=item,
                            price=price,
                            quantity=quantity,
                            position=position
                        )
                        position += 1
                
                # Calculate the total amount
                order.calculate_total()
                order.save()
                
                # Clear the session data
                if 'selected_professional_id' in self.request.session:
                    del self.request.session['selected_professional_id']
                if 'selected_items' in self.request.session:
                    del self.request.session['selected_items']
                
                messages.success(self.request, f"Order #{order.pk} has been created successfully.")
                return redirect('orders:order_detail', order.pk)
                
        except Exception as e:
            messages.error(self.request, f"An error occurred while creating the order: {str(e)}")
            return self.form_invalid(form)

class AgentEditOrderView(AgentRequiredMixin, UpdateView):
    """View for agents to edit an existing order."""
    model = Order
    form_class = AgentOrderForm
    template_name = 'users/agent_edit_order.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        # Only allow editing orders created by this agent
        return Order.objects.filter(agent=self.request.user.agent_profile)
    
    def get_success_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f"Order #{self.object.pk} has been updated successfully.")
        return super().form_valid(form)

