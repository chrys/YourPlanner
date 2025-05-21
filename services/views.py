from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from users.models import Professional
from .models import Service, Item, Price 
from .forms import ServiceForm, ItemForm 
from orders.models import OrderItem

# An admin-style page at /services/professional-account/ where a logged-in Professional
# can add and manage their own Services

@login_required
def professional_account(request):
    try:
        professional = request.user.professional_profile
    except Professional.DoesNotExist:
        return render(request, 'services/not_a_professional.html')

    services = Service.objects.filter(professional=professional)

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.professional = professional
            service.save()
            return redirect('professional-account')
    else:
        form = ServiceForm()

    return render(request, 'services/professional_account.html', {
        'services': services,
        'form': form,
    })
 
#for each Service where the Professional can add and view Items   
@login_required
def service_items(request, service_id):
    try:
        professional = request.user.professional_profile
    except Professional.DoesNotExist:
        return render(request, 'services/not_a_professional.html')

    service = Service.objects.get(id=service_id, professional=professional)
    items = Item.objects.filter(service=service)

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.service = service
            item.save()
            return redirect('service-items', service_id=service.id)
    else:
        form = ItemForm()

    return render(request, 'services/service_items.html', {
        'service': service,
        'items': items,
        'form': form,
    })
    
#Each item in a Service can be edited or deleted
@login_required
def edit_item(request, item_id):
    item = Item.objects.get(pk=item_id)
    active_price = item.prices.filter(is_active=True).first()
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            if active_price:
                active_price.amount = request.POST.get('active_price_amount')
                active_price.currency = request.POST.get('active_price_currency')
                active_price.frequency = request.POST.get('active_price_frequency')
                active_price.save()
            # Instead of redirect, just render the same page
            return render(request, 'services/edit_item.html', {
                'form': form,
                'item': item,
                'active_price': active_price,
                'saved': True,  # Optional: pass a flag if you want
            })
    else:
        form = ItemForm(instance=item)
    return render(request, 'services/edit_item.html', {'form': form, 'item': item, 'active_price': active_price})

@login_required
@csrf_protect
def delete_service(request, service_id):
    try:
        professional = request.user.professional_profile
    except Professional.DoesNotExist:
        return render(request, 'services/not_a_professional.html')

    service = get_object_or_404(Service, id=service_id, professional=professional)
    
    # Check if any items from this service are in a customer's basket
    items_in_basket = OrderItem.objects.filter(service=service).exists()
    
    if items_in_basket:
        # Get the list of customers who have this service in their basket
        customers_with_service = OrderItem.objects.filter(service=service).values_list('order__customer__user__username', flat=True).distinct()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'This service cannot be deleted because it exists in customer baskets.',
                'customers': list(customers_with_service)
            })
        
        messages.error(request, f"This service cannot be deleted because it exists in customer baskets. Customers: {', '.join(customers_with_service)}")
        return redirect('professional-account')
    
    # If no items in basket, proceed with deletion
    service.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, f"Service '{service.title}' has been deleted successfully.")
    return redirect('professional-account')

@login_required
@csrf_protect
def delete_item(request, item_id):
    try:
        professional = request.user.professional_profile
    except Professional.DoesNotExist:
        return render(request, 'services/not_a_professional.html')

    item = get_object_or_404(Item, id=item_id, service__professional=professional)
    service_id = item.service.id
    
    # Check if this item is in a customer's basket
    item_in_basket = OrderItem.objects.filter(item=item).exists()
    
    if item_in_basket:
        # Get the list of customers who have this item in their basket
        customers_with_item = OrderItem.objects.filter(item=item).values_list('order__customer__user__username', flat=True).distinct()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'This item cannot be deleted because it exists in customer baskets.',
                'customers': list(customers_with_item)
            })
        
        messages.error(request, f"This item cannot be deleted because it exists in customer baskets. Customers: {', '.join(customers_with_item)}")
        return redirect('service-items', service_id=service_id)
    
    # If not in basket, proceed with deletion
    item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, f"Item '{item.title}' has been deleted successfully.")
    return redirect('service-items', service_id=service_id)
