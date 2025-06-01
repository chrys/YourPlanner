from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch, F, Sum, DecimalField, ExpressionWrapper
from django.core.cache import cache
from users.models import ProfessionalCustomerLink
from services.models import Service, Item, Price
from .models import Order, OrderItem

import logging

logger = logging.getLogger('orders')

'''
Each Customer can select a Professional and then select items from that Professional.
Update the select_items view to update the basket in-place
Remove all existing OrderItems for the order before adding new ones, 
or update quantities if the item already exists.
After POST, stay on the same page (do not redirect to basket).
'''
@login_required
def select_items(request):
    # Get the customer profile from the request
    # Get their professional link 
    customer = request.user.customer_profile
    link = ProfessionalCustomerLink.objects.filter(
        customer=customer, 
        status=ProfessionalCustomerLink.StatusChoices.ACTIVE
    ).select_related('professional').first()
    
    # If no link is found, redirect to user management page
    if not link:
        logger.warning(f"No active professional link found for customer user {customer.user.username}")
        return redirect('user_management')

    professional = link.professional
    
    # Get or create an order for the customer
    order, created = Order.objects.get_or_create(
        customer=customer,
        status=Order.StatusChoices.CONFIRMED 
    )
    if not order:
        logger.warning(f"Order not found for customer {customer.id}")
    
    # Cache key for services
    cache_key = f'professional_services_{professional.pk}_{professional.updated_at.timestamp()}'
    services = cache.get(cache_key)
    
    if services is None:
        # Get all services and items for the professional with efficient prefetching
        services = Service.objects.filter(
            professional=professional, 
            is_active=True
        ).prefetch_related(
            Prefetch('items', queryset=Item.objects.prefetch_related(
                Prefetch('prices', queryset=Price.objects.filter(is_active=True))
            ))
        )
        # Cache for 5 minutes
        cache.set(cache_key, services, 60 * 5)

    # Get current quantities for display
    current_quantities = {
        str(oi.item_id): oi.quantity 
        for oi in order.items.all()
    }
    logger.debug(f"Current quantities for order {order.id}: {current_quantities}")

    if request.method == 'POST':
        with transaction.atomic():
            for service in services:
                for item in service.items.all():
                    qty = int(request.POST.get(f'item_{item.id}', 0))
                    price = item.prices.filter(is_active=True).first()
                    order_item = order.items.filter(item=item).first()
                    if qty > 0:
                        if not price:
                            # Skip items with no active price
                            logger.warning(f"Item {item.id} has no active price, skipping")
                            continue
                        if order_item:
                            # Update existing item
                            order_item.quantity = qty
                            order_item.price = price
                            order_item.price_amount_at_order = price.amount
                            order_item.price_currency_at_order = price.currency
                            order_item.price_frequency_at_order = price.frequency
                            order_item.save()
                        else:
                            # Create new item
                            OrderItem.objects.create(
                                order=order,
                                professional=professional,
                                service=service,
                                item=item,
                                price=price,
                                quantity=qty,
                                price_amount_at_order=price.amount,
                                price_currency_at_order=price.currency,
                                price_frequency_at_order=price.frequency
                            )
                    elif order_item:
                        # Remove item if quantity is zero
                        order_item.delete()   

            # Update the current quantities after processing
            current_quantities = {
                str(oi.item_id): oi.quantity 
                for oi in order.items.all()
            }
            
            # Calculate and update order total
            order.calculate_total()

    return render(request, 'orders/select_items.html', {
        'services': services,
        'order': order,
        'current_quantities': current_quantities,
    })   

'''
A page called Basket will display the OrderItems chosen by the User with their prices
and at the end the Total Price which will be the sum of all prices.
'''    
@login_required
def basket(request):
    customer = request.user.customer_profile
    order = Order.objects.filter(
        customer=customer, 
        status=Order.StatusChoices.CONFIRMED
    ).prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.select_related(
            'service', 'item', 'price', 'professional'
        ))
    ).first()
    
    if not order:
        return render(request, 'orders/basket.html', {
            'order': None,
            'items': [],
            'total': 0,
        })
    
    items = order.items.all()
    
    # Calculate total using efficient database aggregation
    total = items.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('quantity') * F('price_amount_at_order'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
    )['total'] or 0
    
    return render(request, 'orders/basket.html', {
        'order': order,
        'items': items,
        'total': total,
    })
