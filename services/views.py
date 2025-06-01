from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.db.models import Prefetch
from django.core.cache import cache
from users.models import Professional
from .models import Service, Item, Price 
from .forms import ServiceForm, ItemForm, PriceForm
from orders.models import OrderItem


@login_required
def service_items(request, service_id):
    try:
        professional = request.user.professional_profile
    except Professional.DoesNotExist:
        return render(request, 'services/not_a_professional.html')

    service = get_object_or_404(Service, id=service_id, professional=professional)
    
    # Cache key for items
    cache_key = f'service_items_{service.pk}_{service.updated_at.timestamp()}'
    items = cache.get(cache_key)
    
    if items is None:
        items = Item.objects.filter(service=service).prefetch_related('prices')
        cache.set(cache_key, items, 60 * 10)  # Cache for 10 minutes

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        price_form = PriceForm(request.POST)
        if form.is_valid() and price_form.is_valid():
            with transaction.atomic():
                item = form.save(commit=False)
                item.service = service
                item.save()
                # Save the price
                price = price_form.save(commit=False)
                price.item = item
                price.is_active = True
                price.save()
                # Invalidate cache
                cache.delete(cache_key)
            return redirect('service-items', service_id=service.id)
    else:
        form = ItemForm()
        price_form = PriceForm()

    return render(request, 'services/service_items.html', {
        'service': service,
        'items': items,
        'form': form,
        'price_form': price_form,
    })

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    # Ensure the user owns this item
    if item.service.professional.user != request.user:
        messages.error(request, "You don't have permission to edit this item.")
        return redirect('professional-account')
        
    active_price = item.prices.filter(is_active=True).first()

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        price_form = PriceForm(request.POST, instance=active_price)
        if form.is_valid() and price_form.is_valid():
            with transaction.atomic():
                form.save()
                price = price_form.save(commit=False)
                price.item = item
                price.is_active = True
                price.save()
                # Invalidate cache
                cache.delete(f'service_items_{item.service.pk}_{item.service.updated_at.timestamp()}')
            return render(request, 'services/edit_item.html', {
                'form': form,
                'price_form': price_form,
                'item': item,
                'saved': True,
            })
    else:
        form = ItemForm(instance=item)
        price_form = PriceForm(instance=active_price)

    return render(request, 'services/edit_item.html', {
        'form': form,
        'price_form': price_form,
        'item': item,
    })

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
        customers_with_service = OrderItem.objects.filter(service=service).values_list('order__customer__user__username', flat=True).distinct()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'This service cannot be deleted because it exists in customer baskets.',
                'customers': list(customers_with_service)
            })
        messages.error(request, "Cannot Delete Service. Please ask them to remove the items from their basket first.")
        return redirect('professional-account')
    
    # If no items in basket, proceed with deletion
    with transaction.atomic():
        service.delete()
        # Invalidate cache
        cache.delete(f'professional_services_{professional.pk}_{professional.updated_at.timestamp()}')
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, "Service Deleted")
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
        customers_with_item = OrderItem.objects.filter(item=item).values_list('order__customer__user__username', flat=True).distinct()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'This item cannot be deleted because it exists in customer baskets.',
                'customers': list(customers_with_item)
            })
        messages.error(request, "Cannot Delete Item. Please ask them to remove the item from their basket first.")
        return redirect('service-items', service_id=service_id)
    
    # If not in basket, proceed with deletion
    with transaction.atomic():
        item.delete()
        # Invalidate cache
        cache.delete(f'service_items_{service_id}_{item.service.updated_at.timestamp()}')
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, "Item Deleted")
    return redirect('service-items', service_id=service_id)

@login_required
def professional_account(request):
    """
    View for professional's account dashboard. Shows services and allows creating new ones.
    """
    try:
        professional = request.user.professional_profile
    except Professional.DoesNotExist:
        return render(request, 'services/not_a_professional.html')

    # Cache key for services
    cache_key = f'professional_services_{professional.pk}_{professional.updated_at.timestamp()}'
    services = cache.get(cache_key)
    
    if services is None:
        services = Service.objects.filter(professional=professional).prefetch_related(
            Prefetch('items', queryset=Item.objects.prefetch_related('prices'))
        )
        cache.set(cache_key, services, 60 * 10)  # Cache for 10 minutes

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    service = form.save(commit=False)
                    service.professional = professional
                    service.full_clean()
                    service.save()
                    # Invalidate cache
                    cache.delete(cache_key)
                messages.success(request, "Service created successfully")
                return redirect('professional-account')
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
    else:
        form = ServiceForm()

    context = {
        'services': services,
        'form': form,
        'professional': professional,
    }
    
    return render(request, 'services/professional_account.html', context)