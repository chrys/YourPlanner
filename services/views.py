# pyright: reportAttributeAccessIssue=false
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.http import Http404 
from django.contrib import messages
from django.core.exceptions import ValidationError
from users.models import Professional
from .models import Service, Item, Price
from .forms import ServiceForm, ItemForm, PriceForm, ServicePriceFormSet
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # CHANGED: Import for type checking only
    pass


class ProfessionalRequiredMixin(UserPassesTestMixin):
    """
    Ensures the logged-in user has a professional profile.
    """
    def test_func(self):
        try:
            return hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None
        except Professional.DoesNotExist:
            return False

    def handle_no_permission(self):
        messages.error(self.request, "You are not registered as a professional.")
        # Redirect to a page explaining they need to be a professional or to create a profile
        # For now, redirect to login, or a dedicated 'not_professional_page'
        return redirect('users:profile_choice') # Assuming 'users:profile_choice' or similar exists

class ProfessionalOwnsObjectMixin(UserPassesTestMixin):
    """
    Mixin to verify that the request.user's professional_profile owns the object.
    Assumes the view's model has a 'professional' field.
    """
    def test_func(self):
        obj = self.get_object()
        try:
            professional = self.request.user.professional_profile
            return obj.professional == professional
        except Professional.DoesNotExist:
            return False # Should not happen if ProfessionalRequiredMixin is also used

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to modify or delete this service.")
        # Consider redirecting to the object's detail page or a list view
        return redirect(reverse_lazy('services:service_list'))


class UserOwnsParentServiceMixin(UserPassesTestMixin):
    """
    Mixin to verify that the request.user's professional_profile owns the parent Service
    of an Item or Price. Requires `self.kwargs['service_pk']` to be present in the URL.
    It also fetches and stores `self.service` on the view.
    """
    def dispatch(self, request, *args, **kwargs):
        service_pk = self.kwargs.get('service_pk')
        if not service_pk:
            raise Http404("Service PK not found in URL.")
        try:
            professional = self.request.user.professional_profile
            self.service = get_object_or_404(Service, pk=service_pk, professional=professional)
        except Professional.DoesNotExist:
            self.service = None
        except Http404:
            self.service = None
        return super().dispatch(request, *args, **kwargs)
    
    def test_func(self):
        return self.service is not None

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access items for this service.")
        return redirect(reverse_lazy('services:service_list'))


class UserOwnsGrandparentServiceViaItemMixin(UserPassesTestMixin):
    """
    Mixin to verify that the request.user's professional_profile owns the grandparent Service
    of a Price. Requires `self.kwargs['service_pk']` and `self.kwargs['item_pk']`
    to be present in the URL. It also fetches and stores `self.service` and `self.item`
    on the view.
    """
    def dispatch(self, request, *args, **kwargs):
        service_pk = self.kwargs.get('service_pk')
        item_pk = self.kwargs.get('item_pk')

        if not service_pk or not item_pk:
            raise Http404("Service PK or Item PK not found in URL.")

        try:
            professional = self.request.user.professional_profile
            # Fetch the service and ensure it's owned by the professional
            self.service = get_object_or_404(Service, pk=service_pk, professional=professional)
            # Fetch the item and ensure it belongs to the fetched service
            self.item = get_object_or_404(Item, pk=item_pk, service=self.service)
        except Professional.DoesNotExist:
            self.service = None
            self.item = None
        except Http404:
            self.service = None
            self.item = None

        # Always return the result of super().dispatch
        return super().dispatch(request, *args, **kwargs)
            
    def test_func(self):
        return self.service is not None and self.item is not None

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access prices for this item/service.")
        return redirect(reverse_lazy('services:service_list'))


# Service CBVs

class ServiceCreateView(LoginRequiredMixin, ProfessionalRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'services/service_form.html'
    success_url = reverse_lazy('services:service_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # CHANGED: Added formset for multiple service-level prices
        if self.request.POST:
            # CHANGED: Pass POST data but only use instance if it exists
            if self.object and self.object.pk:
                context['formset'] = ServicePriceFormSet(self.request.POST, instance=self.object)
            else:
                context['formset'] = ServicePriceFormSet(self.request.POST)
        else:
            # CHANGED: Only pass instance if creating with existing data
            if hasattr(self, 'object') and self.object and self.object.pk:
                context['formset'] = ServicePriceFormSet(instance=self.object)
            else:
                context['formset'] = ServicePriceFormSet()
        context['page_title'] = "Create New Service"
        return context

    def form_valid(self, form):
        try:
            professional = self.request.user.professional_profile
        except Professional.DoesNotExist:
            # This should ideally be caught by ProfessionalRequiredMixin
            messages.error(self.request, "You must have a professional profile to create a service.")
            return self.form_invalid(form)
        form.instance.professional = professional
        
        # CHANGED: Handle price formset - save service first, then prices
        self.object = form.save()  # Save the service first
        
        # Now get the formset with the saved object
        context = self.get_context_data()
        formset = context['formset']
        
        # Re-bind formset with POST data and instance
        if self.request.POST:
            formset = ServicePriceFormSet(self.request.POST, instance=self.object)
        
        if formset.is_valid():
            formset.save()
            messages.success(self.request, "Service created successfully with prices.")
            return super().form_valid(form)
        else:
            # If formset is invalid, delete the service and show errors
            self.object.delete()
            # Re-attach formset errors to context
            context['formset'] = formset
            return self.render_to_response(context)

class ServiceListView(LoginRequiredMixin, ListView):
    model = Service
    template_name = 'services/service_list.html' # Or 'services/professional_account.html' if it becomes the list view
    context_object_name = 'services'

    def get_queryset(self):
        try:
            professional = self.request.user.professional_profile
            # Professionals see only their services
            return Service.objects.owned_by(professional).order_by('-created_at')
        except Professional.DoesNotExist:
            return Service.objects.none() # Or raise Http404 or redirect

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['professional'] = self.request.user.professional_profile
        except Professional.DoesNotExist:
            context['professional'] = None # Should not happen if get_queryset returns none for non-pros
        context['page_title'] = "My Services"
        return context

class ServiceDetailView(LoginRequiredMixin, DetailView): # Potentially add permission mixin if details are private
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'

    def get_queryset(self):
        # Allow viewing if user is the professional owner or if service is active (for potential customers)
        # For now, only owner can view for simplicity, matching ProfessionalOwnsObjectMixin logic
        # If customers can view, this would need adjustment.
        qs = super().get_queryset()
        try:
            professional = self.request.user.professional_profile
            return qs.filter(professional=professional) # Owner can see active/inactive
        except Professional.DoesNotExist:
             # If regular users should see active services:
             # return qs.filter(is_active=True)
            return qs.none() # For now, only professional can view their service details

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.get_object()
        # Example of how items might be passed if not handled by template relations directly
        # context['items'] = Item.objects.filter(service=service).prefetch_related('prices')
        context['page_title'] = service.title
        # CHANGED: Add service prices to context
        context['service_prices'] = service.get_service_prices().prefetch_related('labels')
        # Check if the current user owns this service to show/hide edit/delete buttons in template
        try:
            context['user_owns_service'] = (self.request.user.professional_profile == service.professional)
        except Professional.DoesNotExist:
            context['user_owns_service'] = False
        return context

class ServiceUpdateView(LoginRequiredMixin, ProfessionalRequiredMixin, ProfessionalOwnsObjectMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'services/service_form.html'
    # success_url is dynamically set in get_success_url

    def get_success_url(self):
        return reverse_lazy('services:service_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # CHANGED: Added formset for multiple service-level prices
        if self.request.POST:
            context['formset'] = ServicePriceFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ServicePriceFormSet(instance=self.object)
        context['page_title'] = f"Edit Service: {self.object.title}"
        return context

    def form_valid(self, form):
        # CHANGED: Handle price formset - save form first, then formset
        self.object = form.save()
        
        # Re-bind formset with POST data and updated instance
        if self.request.POST:
            formset = ServicePriceFormSet(self.request.POST, instance=self.object)
        else:
            formset = ServicePriceFormSet(instance=self.object)
        
        if formset.is_valid():
            formset.save()
            messages.success(self.request, "Service updated successfully with prices.")
            return super().form_valid(form)
        else:
            # If formset is invalid, show errors
            context = self.get_context_data()
            context['formset'] = formset
            return self.render_to_response(context)

class ServiceDeleteView(LoginRequiredMixin, ProfessionalRequiredMixin, ProfessionalOwnsObjectMixin, DeleteView):
    model = Service
    template_name = 'services/service_confirm_delete.html'
    success_url = reverse_lazy('services:service_list')
    context_object_name = 'service'

    def form_valid(self, form):
        # Add check for items in basket before deletion (TODO)
        # For now, directly delete.
        # service = self.get_object()
        # items_in_basket = OrderItem.objects.filter(service=service).exists()
        # if items_in_basket:
        #     messages.error(self.request, "This service cannot be deleted because its items are in customer baskets.")
        #     return redirect('services:service_detail', pk=service.pk)
        messages.success(self.request, f"Service '{self.object.title}' deleted successfully.")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Delete Service: {self.object.title}"
        return context



class ItemCreateView(LoginRequiredMixin, ProfessionalRequiredMixin, UserOwnsParentServiceMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'services/item_form.html'
    # success_url is dynamically set in get_success_url

    def form_valid(self, form):
        # self.service is set by UserOwnsParentServiceMixin's test_func via dispatch
        form.instance.service = self.service
        messages.success(self.request, f"Item '{form.instance.title}' created for service '{self.service.title}'.")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the parent service's detail page
        return reverse_lazy('services:service_detail', kwargs={'pk': self.service.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.service should be set by UserOwnsParentServiceMixin's test_func called during dispatch
        context['service'] = self.service
        context['page_title'] = f"Add Item to {self.service.title}"
        return context

class ItemListView(LoginRequiredMixin, ProfessionalRequiredMixin, UserOwnsParentServiceMixin, ListView):
    model = Item
    template_name = 'services/item_list.html' # Or integrate into service_detail
    context_object_name = 'items'

    def dispatch(self, request, *args, **kwargs):
        # Ensure UserOwnsParentServiceMixin's test_func is called to set self.service
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # self.service is set by UserOwnsParentServiceMixin
        return Item.objects.filter(service=self.service).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        context['page_title'] = f"Items for {self.service.title}" # type: ignore
        return context

class ItemDetailView(LoginRequiredMixin, ProfessionalRequiredMixin, UserOwnsParentServiceMixin, DetailView):
    model = Item
    template_name = 'services/item_detail.html'
    context_object_name = 'item'
    # pk_url_kwarg = 'item_pk' # if your URL uses 'item_pk' instead of 'pk'

    def dispatch(self, request, *args, **kwargs):
        # Ensure UserOwnsParentServiceMixin's test_func is called to set self.service
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Filter items by the service obtained in UserOwnsParentServiceMixin
        # This ensures the item belongs to the specified service and thus the professional
        return Item.objects.filter(service=self.service, pk=self.kwargs.get('pk'))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service # self.service set by mixin
        # item is self.object, already in context
        context['page_title'] = f"Item: {self.object.title}"
        # Check for ownership for edit/delete buttons in template
        context['user_owns_service'] = True # Since UserOwnsParentServiceMixin passed
        return context

class ItemUpdateView(LoginRequiredMixin, ProfessionalRequiredMixin, UserOwnsParentServiceMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'services/item_form.html'
    # pk_url_kwarg = 'item_pk'

    def dispatch(self, request, *args, **kwargs):
        # Ensure UserOwnsParentServiceMixin's test_func is called to set self.service
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Item.objects.filter(service=self.service, pk=self.kwargs.get('pk'))

    def get_success_url(self):
        return reverse_lazy('services:item_detail', kwargs={'service_pk': self.service.pk, 'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f"Item '{form.instance.title}' updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        context['page_title'] = f"Edit Item: {self.object.title}"
        return context

class ItemDeleteView(LoginRequiredMixin, ProfessionalRequiredMixin, UserOwnsParentServiceMixin, DeleteView):
    model = Item
    template_name = 'services/item_confirm_delete.html'
    context_object_name = 'item'
    # pk_url_kwarg = 'item_pk'

    def dispatch(self, request, *args, **kwargs):
        # Ensure UserOwnsParentServiceMixin's test_func is called to set self.service
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Item.objects.filter(service=self.service, pk=self.kwargs.get('pk'))

    def get_success_url(self):
        # Redirect to the parent service's detail page after deleting an item
        return reverse_lazy('services:service_detail', kwargs={'pk': self.service.pk})

    def form_valid(self, form):
        # Add check for item in basket before deletion (TODO)
        messages.success(self.request, f"Item '{self.object.title}' deleted successfully from service '{self.service.title}'.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        context['page_title'] = f"Delete Item: {self.object.title}"
        return context


class PriceCreateView(LoginRequiredMixin, ProfessionalRequiredMixin, UserOwnsGrandparentServiceViaItemMixin, CreateView):
    model = Price
    form_class = PriceForm
    template_name = 'services/price_form.html'

    def dispatch(self, request, *args, **kwargs):
        # UserOwnsGrandparentServiceViaItemMixin's test_func sets self.service and self.item
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.item = self.item # self.item is set by the mixin
        # CHANGED: Simply save the form - item has been set by the view
        messages.success(self.request, f"Price created for item '{self.item.title}'.")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the parent item's detail page
        return reverse_lazy('services:item_detail', kwargs={'service_pk': self.service.pk, 'pk': self.item.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        context['item'] = self.item
        context['page_title'] = f"Add Price to {self.item.title} ({self.service.title})"
        return context

class PriceListView(LoginRequiredMixin, ProfessionalRequiredMixin, UserOwnsGrandparentServiceViaItemMixin, ListView):
    model = Price
    template_name = 'services/price_list.html' # Or integrate into item_detail
    context_object_name = 'prices'
    service: Service
    item: Item

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Use custom queryset method instead of filter()
        return Price.objects.for_item(self.item).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # CHANGED: Add active prices and valid prices for display
        context['service'] = self.service
        context['item'] = self.item
        context['active_prices'] = self.item.get_active_prices()
        context['valid_prices'] = self.item.get_valid_prices()
        context['page_title'] = f"Prices for {self.item.title}"
        return context

class PriceDetailView(LoginRequiredMixin, ProfessionalRequiredMixin, UserOwnsGrandparentServiceViaItemMixin, DetailView):
    model = Price
    template_name = 'services/price_detail.html'
    context_object_name = 'price'
    # pk_url_kwarg = 'price_pk' for URL

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Price 'pk' (or 'price_pk') is from URL, item from mixin
        return Price.objects.filter(item=self.item, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        context['item'] = self.item
        # price is self.object, already in context
        context['page_title'] = f"Price Details for {self.item.title}"
        context['user_owns_service'] = True # Since mixin passed
        return context

class PriceUpdateView(LoginRequiredMixin, ProfessionalRequiredMixin, UserOwnsGrandparentServiceViaItemMixin, UpdateView):
    model = Price
    form_class = PriceForm
    template_name = 'services/price_form.html'
    # pk_url_kwarg = 'price_pk'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Price.objects.filter(item=self.item, pk=self.kwargs.get('pk'))

    def get_success_url(self):
        return reverse_lazy('services:price_detail', kwargs={'service_pk': self.service.pk, 'item_pk': self.item.pk, 'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Price updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        context['item'] = self.item
        context['page_title'] = f"Edit Price for {self.item.title}"
        return context

class PriceDeleteView(LoginRequiredMixin, ProfessionalRequiredMixin, UserOwnsGrandparentServiceViaItemMixin, DeleteView):
    model = Price
    template_name = 'services/price_confirm_delete.html'
    context_object_name = 'price'
    # pk_url_kwarg = 'price_pk'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Price.objects.filter(item=self.item, pk=self.kwargs.get('pk'))

    def get_success_url(self):
        # Redirect to the parent item's detail page
        return reverse_lazy('services:item_detail', kwargs={'service_pk': self.service.pk, 'pk': self.item.pk})

    def form_valid(self, form):
        messages.success(self.request, f"Price deleted successfully from item '{self.item.title}'.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        context['item'] = self.item
        context['page_title'] = f"Delete Price for {self.item.title}"
        return context


# CHANGED: Added Food & Drinks page view for customers
class FoodDrinksView(LoginRequiredMixin, TemplateView):
    """View to display Food & Drinks items organized by category labels."""
    template_name = 'services/food_drinks.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # CHANGED: Map section names to label names
        sections = {
            'Getting Ready': 'Getting Ready',
            'On Arrival Drinks': 'Drink On Arrival',
            'Reception Drinks & Canapes': 'On Reception',
            'Drinks During Dinner': 'On Dinner',
            'Pre Wedding BBQ': 'Pre Wedding BBQ',
            'Country Menu': 'On Country Menu',
            'Village BBQ': 'On Village BBQ',
            'Mediterranean Flavors': 'On Mediterranean Flavors',
            'Kids Menu': 'Kids Menu',
            'Evening Buffet Menu': 'Evening Buffet',
            'Supplier Meal': 'Supplier Meal',
        }
        
        # CHANGED: Get items by label for each section (not tied to a service)
        food_drinks_sections = {}
        for section_name, label_name in sections.items():
            items = Item.objects.filter(
                labels__name=label_name,
                is_active=True
            ).distinct()
            food_drinks_sections[section_name] = items
        
        context['food_drinks_sections'] = food_drinks_sections
        context['page_title'] = "Food & Drinks"
        return context
