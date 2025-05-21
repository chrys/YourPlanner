from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from users.models import Professional
from .models import Service, Item, Price 
from .forms import ServiceForm, ItemForm, PriceForm
from orders.models import OrderItem

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
 

@login_required
def service_items(request, service_id):
    try:
        professional = request.user.professional_profile
    except Professional.DoesNotExist:
        return render(request, 'services/not_a_professional.html')

    service = Service.objects.get(id=service_id, professional=professional)
    items = Item.objects.filter(service=service)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.service = service
            item.save()
            # Save the price
            Price.objects.create(
                item=item,
                amount=form.cleaned_data['price_amount'],
                currency=form.cleaned_data['price_currency'],
                frequency=form.cleaned_data['price_frequency'],
                is_active=True
            )
            return redirect('service-items', service_id=service.id)
    else:
        form = ItemForm()

    return render(request, 'services/service_items.html', {
        'service': service,
        'items': items,
        'form': form,
    })

@login_required
def edit_item(request, item_id):
    item = Item.objects.get(pk=item_id)
    active_price = item.prices.filter(is_active=True).first()
    from .forms import PriceForm  # Make sure this is imported

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        price_form = PriceForm(request.POST, instance=active_price)
        if form.is_valid() and price_form.is_valid():
            form.save()
            price = price_form.save(commit=False)
            price.item = item
            price.is_active = True
            price.save()
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
    service.delete()
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
    item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, "Item Deleted")
    return redirect('service-items', service_id=service_id)