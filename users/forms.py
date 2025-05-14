from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('professional', 'Professional'),
    )
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']