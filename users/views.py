from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .forms import RegistrationForm
from .models import Professional, Customer
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
                Professional.objects.create(user=user)
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('user_management')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})


#This function will handle displaying the user management page and login form
def user_management_view(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_management')
            else:
                messages.error(request, 'Invalid username or password.')
        return render(request, 'users/login.html')
    return render(request, 'users/management.html')
