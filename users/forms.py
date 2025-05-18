from django import forms
from django.contrib.auth.models import User
from .models import Professional

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
    title = forms.CharField(max_length=200, required=False)  # Only for professionals


    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']
        
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        title = cleaned_data.get('title')
        if role == 'professional' and not title:
            self.add_error('title', 'Title is required for professionals.')
        return cleaned_data
    
class ProfessionalChoiceForm(forms.Form):
    professional = forms.ModelChoiceField(
        queryset=Professional.objects.all(),
        required=True,
        label="Choose your Professional",
        widget=forms.Select(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['professional'].label_from_instance = lambda obj: obj.title or obj.user.get_full_name() or obj.user.username