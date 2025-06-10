from django import forms
from django.contrib.auth.models import User
from .models import Professional, Customer
from labels.models import Label
from django.utils import timezone 

class RegistrationForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('professional', 'Professional'),
        ('agent', 'Agent'),
    )
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    title = forms.CharField(max_length=200, required=False)  # Only for professionals
    wedding_day = forms.DateField(
        required=False,  # Will be made required conditionally in clean method
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Required if registering as a customer."
    )
    # labels = forms.ModelMultipleChoiceField(
    #     queryset=Label.objects.all(),
    #     required=False,
    #     widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
    #     help_text="Optional labels to categorize this user"
    # )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']
        
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        title = cleaned_data.get('title')
        wedding_day = cleaned_data.get('wedding_day')

        if role == 'professional' and not title:
            self.add_error('title', 'Title is required for professionals.')
        
        if role == 'customer':
            if not wedding_day:
                self.add_error('wedding_day', 'Wedding day is required for customers.')
            elif wedding_day <= timezone.now().date(): # This should catch it
                self.add_error('wedding_day', 'The wedding day must be in the future.')
        
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

class ProfessionalForm(forms.ModelForm):
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.filter(label_type='PROFESSIONAL'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select labels relevant to this professional profile."
    )

    class Meta:
        model = Professional
        fields = [
            'title', 'specialization', 'bio', 'profile_image',
            'contact_hours', 'rating', 'labels'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'contact_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CustomerForm(forms.ModelForm):
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.filter(label_type='CUSTOMER'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select labels relevant to this customer profile."
    )

    class Meta:
        model = Customer
        fields = [
            'company_name', 'shipping_address', 'billing_address',
            'preferred_currency', 'marketing_preferences', 'labels'
        ]  # Intentionally excluding 'role' field to make it inaccessible to customers
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'billing_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preferred_currency': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 3}), # Using TextInput
            'marketing_preferences': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CustomerLabelForm(forms.ModelForm):
    """Form for updating customer labels."""
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.filter(label_type='CUSTOMER'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select labels for this customer."
    )
    
    class Meta:
        model = Customer
        fields = ['labels']


class DepositPaymentForm(forms.Form):
    deposit_paid_checkbox = forms.BooleanField(label="I have paid the deposit", required=True)
