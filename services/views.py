from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from users.models import Professional
from .models import Service, Item, Price 
from .forms import ServiceForm, ItemForm 

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