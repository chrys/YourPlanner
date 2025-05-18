from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from .models import Professional, Customer, ProfessionalCustomerLink
from orders.models import Order, OrderItem
from django import forms
from .forms import RegistrationForm, ProfessionalChoiceForm
#simple registration page in your users app where a user can register as either a professional or a customer 
# using their name and email, using Django's built-in User model and forms. 

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password'],
            )
            role = form.cleaned_data['role']
            if role == 'customer':
                Customer.objects.create(user=user)
            else:
                Professional.objects.create(
                    user=user,
                    title=form.cleaned_data['title']
                )
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('user_management')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})




'''
This view handles the user management page. It checks if the user is a customer 
and if they are already linked to a professional.
users/management.html will be shown if the user is a Professional 
users/customer_dashboard.html will be shown if the user is a Customer and already linked to a Professional
If the user is a Customer and not linked to a Professional,
they will be shown a form to select a Professional.
'''
@login_required
def user_management_view(request):
    user = request.user
    # Check if user is a Customer
    try:
        customer = user.customer_profile
    except Customer.DoesNotExist:
        # Not a customer, show default management page
        return render(request, 'users/management.html')

    # Check if customer already linked to a professional
    link = ProfessionalCustomerLink.objects.filter(customer=customer, status=ProfessionalCustomerLink.StatusChoices.ACTIVE).first()
    if not link:
        # Show professional selection form
        if request.method == 'POST':
            form = ProfessionalChoiceForm(request.POST)
            if form.is_valid():
                professional = form.cleaned_data['professional']
                ProfessionalCustomerLink.objects.create(
                    professional=professional,
                    customer=customer,
                    status=ProfessionalCustomerLink.StatusChoices.ACTIVE
                )
                return redirect('select-items')
        else:
            form = ProfessionalChoiceForm()
        return render(request, 'users/customer_choose_professional.html', {'form': form})

    # If already linked, show customer dashboard
    return render(request, 'users/customer_dashboard.html', {'professional': link.professional})


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


@login_required
def change_professional(request):
    user = request.user
    try:
        customer = user.customer_profile
    except Customer.DoesNotExist:
        return redirect('user_management')

    # Deactivate or delete the current link
    ProfessionalCustomerLink.objects.filter(
        customer=customer,
        status=ProfessionalCustomerLink.StatusChoices.ACTIVE
    ).delete()  # Or update status if you want to keep history

    # Show the professional selection form
    if request.method == 'POST':
        form = ProfessionalChoiceForm(request.POST)
        if form.is_valid():
            professional = form.cleaned_data['professional']
            ProfessionalCustomerLink.objects.create(
                professional=professional,
                customer=customer,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            )
            return redirect('user_management')
    else:
        form = ProfessionalChoiceForm()
    return render(request, 'users/customer_choose_professional.html', {'form': form})