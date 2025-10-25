import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import (
    BasketTemplateForm, 
    BasketServiceForm, 
    UpdateGuestCountForm, 
    UpdateItemQuantityForm
)
from .models import Basket, BasketTemplate, BasketService, BasketItem
from services.models import Service
from packages.models import Template

logger = logging.getLogger(__name__)

class SelectTemplateView(View):
    def get(self, request):
        form = BasketTemplateForm()
        return render(request, 'basket/select_template.html', {'form': form})

    def post(self, request):
        form = BasketTemplateForm(request.POST)
        if form.is_valid():
            template = form.cleaned_data['template']
            guest_count = form.cleaned_data['guest_count']
            
            if request.user.is_authenticated:
                basket, created = Basket.objects.get_or_create(customer=request.user, defaults={'guest_count': guest_count})
                if created:
                    logger.info(f"New basket created for user {request.user.username}")
                basket.guest_count = guest_count
                basket.save()
                
                BasketTemplate.objects.create(basket=basket, template=template)
                logger.info(f"Template {template.id} added to basket {basket.id} for user {request.user.username}")

                for service in template.services.all():
                    BasketService.objects.create(
                        basket=basket,
                        service=service,
                        price=service.price
                    )
                
                basket.update_total()
                return redirect('basket:view_basket')
            else:
                logger.warning("Unauthenticated user tried to create a basket.")
                return redirect('login')
        else:
            logger.warning(f"BasketTemplateForm validation failed: {form.errors.as_json()}")
        
        return render(request, 'basket/select_template.html', {'form': form})

def view_basket(request):
    basket = Basket.objects.filter(customer=request.user).first()
    basket_items = BasketService.objects.filter(basket=basket)
    return render(request, 'basket/view_basket.html', {'basket': basket, 'basket_items': basket_items})

def confirm_basket(request):
    basket = Basket.objects.get(customer=request.user)
    basket.status = 'confirmed'
    basket.save()
    logger.info(f"Basket {basket.id} for user {request.user.username} confirmed.")
    return redirect('basket:view_basket')

class AddServiceToBasketView(View):
    def get(self, request):
        form = BasketServiceForm()
        return render(request, 'basket/add_service.html', {'form': form})

    def post(self, request):
        form = BasketServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.professional = request.user.professional
            service.save()
            basket = Basket.objects.filter(customer=request.user).first()
            if basket:
                BasketService.objects.create(basket=basket, service=service, price=service.price)
                logger.info(f"Service {service.id} added to basket {basket.id} for user {request.user.username}")
                basket.update_total()
            return redirect('basket:view_basket')
        else:
            logger.warning(f"BasketServiceForm validation failed on add: {form.errors.as_json()}")
        return render(request, 'basket/add_service.html', {'form': form})

class EditBasketServiceView(View):
    def get(self, request, service_id):
        basket_service = get_object_or_404(BasketService, id=service_id)
        form = BasketServiceForm(instance=basket_service.service)
        return render(request, 'basket/edit_service.html', {'form': form, 'basket_service': basket_service})

    def post(self, request, service_id):
        basket_service = get_object_or_404(BasketService, id=service_id)
        form = BasketServiceForm(request.POST, instance=basket_service.service)
        if form.is_valid():
            form.save()
            basket_service.price = form.cleaned_data['price']
            basket_service.save()
            logger.info(f"Service {basket_service.id} in basket for user {request.user.username} updated.")
            basket_service.basket.update_total()
            return redirect('basket:view_basket')
        else:
            logger.warning(f"BasketServiceForm validation failed on edit for service {service_id}: {form.errors.as_json()}")
        return render(request, 'basket/edit_service.html', {'form': form, 'basket_service': basket_service})

class DeleteBasketServiceView(View):
    def get(self, request, service_id):
        basket_service = get_object_or_404(BasketService, id=service_id)
        return render(request, 'basket/delete_service.html', {'basket_service': basket_service})

    def post(self, request, service_id):
        basket_service = get_object_or_404(BasketService, id=service_id)
        basket = basket_service.basket
        service_id_log = basket_service.id
        basket_service.delete()
        logger.info(f"Service {service_id_log} deleted from basket {basket.id} for user {request.user.username}")
        basket.update_total()
        return redirect('basket:view_basket')

def update_guest_count(request):
    basket = Basket.objects.get(customer=request.user)
    if request.method == 'POST':
        form = UpdateGuestCountForm(request.POST)
        if form.is_valid():
            basket.guest_count = form.cleaned_data['guest_count']
            basket.save()
            logger.info(f"Guest count for basket {basket.id} for user {request.user.username} updated to {basket.guest_count}.")
            basket.update_total()
            return redirect('basket:view_basket')
        else:
            logger.warning(f"UpdateGuestCountForm validation failed for basket {basket.id}: {form.errors.as_json()}")
    else:
        form = UpdateGuestCountForm(initial={'guest_count': basket.guest_count})
    return render(request, 'basket/update_guest_count.html', {'form': form})

def update_item_quantity(request, item_id):
    item = get_object_or_404(BasketItem, id=item_id)
    if request.method == 'POST':
        form = UpdateItemQuantityForm(request.POST)
        if form.is_valid():
            item.quantity = form.cleaned_data['quantity']
            item.save()
            logger.info(f"Quantity for item {item.id} in basket for user {request.user.username} updated to {item.quantity}.")
            item.basket_service.basket.update_total()
            return redirect('basket:view_basket')
        else:
            logger.warning(f"UpdateItemQuantityForm validation failed for item {item_id}: {form.errors.as_json()}")
    else:
        form = UpdateItemQuantityForm(initial={'quantity': item.quantity})
    return render(request, 'basket/update_item_quantity.html', {'form': form, 'item': item})
