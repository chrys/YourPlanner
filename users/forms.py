from django import forms
from django.contrib.auth.models import User
from .models import Professional, Customer, WeddingTimeline
from labels.models import Label
from django.utils import timezone 


class RegistrationForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('professional', 'Professional'),
    )
    # CHANGED: Made first_name and last_name optional for landing page signup
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        required=True,
        widget=forms.HiddenInput(),  # Hide this field
        initial='customer'  # Set default value
    )
    title = forms.CharField(  # Add title field
        max_length=200,
        required=False,
        help_text="Required for professionals"
    )
    
    wedding_day = forms.DateField(
        required=True,  # Now always required since only customers can register
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Your planned wedding day (must be in the future)."
    )
    
    # CHANGED: Added optional customer fields for signup landing page
    bride_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bride name (optional)'}),
        help_text="Full name of the bride"
    )
    groom_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Groom name (optional)'}),
        help_text="Full name of the groom"
    )
    bride_contact = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bride phone (optional)'}),
        help_text="Bride contact phone number"
    )
    groom_contact = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Groom phone (optional)'}),
        help_text="Groom contact phone number"
    )

    class Meta:
        model = User
        # CHANGED: Only include fields that are used in the signup form
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if there's no default professional
        if not Professional.objects.filter(default=True).exists():
            # If no default professional, show the role field
            self.fields['role'] = forms.ChoiceField(
                choices=self.ROLE_CHOICES,
                required=True,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
            # Make wedding_day not required initially
            self.fields['wedding_day'].required = False

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        wedding_day = cleaned_data.get('wedding_day')
        title = cleaned_data.get('title')

        if role == 'professional' and not title:
            self.add_error('title', 'Title is required for professionals.')

        if role == 'customer' or Professional.objects.filter(default=True).exists():
            if not wedding_day:
                self.add_error('wedding_day', 'Wedding day is required for customers.')
            elif wedding_day <= timezone.now().date():
                self.add_error('wedding_day', 'The wedding day must be in the future.')

        return cleaned_data
    
class ProfessionalChoiceForm(forms.Form):
    # CHANGED: Added couple_name field (mandatory)
    couple_name = forms.CharField(
        label="Couple's Name",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., John & Jane Smith'
        }),
        help_text="Full names of the couple"
    )
    
    # CHANGED: Added wedding_day field (mandatory, must be in future)
    wedding_day = forms.DateField(
        label="Wedding Day",
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date()  # CHANGED: Enforce future date
        }),
        help_text="The couple's wedding day (must be in the future)"
    )
    
    professional = forms.ModelChoiceField(
        queryset=Professional.objects.all(),
        required=True,
        label="Choose your Professional",
        widget=forms.Select(attrs={'class': 'form-select'}),  # CHANGED: Added Bootstrap class
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['professional'].label_from_instance = lambda obj: obj.title or obj.user.get_full_name() or obj.user.username

    # CHANGED: Added validation for wedding_day
    def clean_wedding_day(self):
        wedding_day = self.cleaned_data.get('wedding_day')
        if wedding_day and wedding_day <= timezone.now().date():
            raise forms.ValidationError("The wedding day must be in the future.")
        return wedding_day

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


class CustomerProfileEditForm(forms.ModelForm):
    # CHANGED: Form for editing customer profile fields (bride/groom details, contacts, emergency contact, planner)
    # CHANGED: wedding_day is excluded - only professionals can edit this field
    class Meta:
        model = Customer
        fields = [
            'bride_name',
            'groom_name',
            'bride_contact',
            'groom_contact',
            'emergency_contact',
            'planner'
        ]
        widgets = {
            'bride_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bride full name'
            }),
            'groom_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Groom full name'
            }),
            'bride_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bride phone number',
                'type': 'tel'
            }),
            'groom_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Groom phone number',
                'type': 'tel'
            }),
            'emergency_contact': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name and phone number',
                'rows': 3
            }),
            'planner': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Wedding planner or coordinator name'
            }),
        }
        labels = {
            'bride_name': 'Bride Name',
            'groom_name': 'Groom Name',
            'bride_contact': 'Bride Contact',
            'groom_contact': 'Groom Contact',
            'emergency_contact': 'Emergency Contact',
            'planner': 'Wedding Planner',
        }


class DepositPaymentForm(forms.Form):
    deposit_paid_checkbox = forms.BooleanField(label="I have paid the deposit", required=True)


class WeddingTimelineForm(forms.ModelForm):
    """
    CHANGED: Form for managing wedding timeline details.
    Updated to include customer profile fields (bride/groom info).
    Organized with Event Details first, then Bride & Groom Information.
    """
    # CHANGED: Added fields from Customer model
    bride_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bride full name'
        }),
        label='Bride Name'
    )
    groom_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Groom full name'
        }),
        label='Groom Name'
    )
    wedding_day_display = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'disabled': True
        }),
        label='Wedding Day'
    )
    bride_contact = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bride phone number',
            'type': 'tel'
        }),
        label='Bride Contact'
    )
    groom_contact = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Groom phone number',
            'type': 'tel'
        }),
        label='Groom Contact'
    )
    emergency_contact = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Emergency contact name and phone number',
            'rows': 3
        }),
        label='Emergency Contact Name & Number'
    )
    planner = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Wedding planner or coordinator name'
        }),
        label='Planner/Coordinator'
    )
    special_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Any special notes for the wedding',
            'rows': 4
        }),
        label='Special Notes'
    )
    
    class Meta:
        model = WeddingTimeline
        fields = [
            'event_organiser_name',
            'contact_number',
            'pre_wedding_appointment',
            'location',
            'apostille_stamp',
            'ceremony_admin',
            'adults',
            'children',
            'babies',
        ]
        widgets = {
            'event_organiser_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event organiser name'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact phone number',
                'type': 'tel'
            }),
            'pre_wedding_appointment': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Wedding venue location'
            }),
            'apostille_stamp': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ceremony_admin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ceremony administrator name'
            }),
            'adults': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Number of adults'
            }),
            'children': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Number of children'
            }),
            'babies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Number of babies'
            }),
        }
        labels = {
            'event_organiser_name': 'Event Organiser Name',
            'contact_number': 'Event Organiser Contact Number',
            'pre_wedding_appointment': 'Pre-Wedding Appointment',
            'location': 'Location',
            'apostille_stamp': 'Apostille stamp service by Vasilias',
            'ceremony_admin': 'Administration of ceremony',
            'adults': 'Number of Adults',
            'children': 'Number of Children',
            'babies': 'Number of Babies',
        }
    
    # CHANGED: Override __init__ to populate fields from customer
    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)
        self._customer = customer  # CHANGED: Store customer as private attribute (can be None)
        if customer:
            # CHANGED: Only set initial values if customer is provided and field exists
            if 'bride_name' in self.fields:
                self.fields['bride_name'].initial = customer.bride_name
            if 'groom_name' in self.fields:
                self.fields['groom_name'].initial = customer.groom_name
            if 'wedding_day_display' in self.fields:
                self.fields['wedding_day_display'].initial = customer.wedding_day
            if 'bride_contact' in self.fields:
                self.fields['bride_contact'].initial = customer.bride_contact
            if 'groom_contact' in self.fields:
                self.fields['groom_contact'].initial = customer.groom_contact
            if 'emergency_contact' in self.fields:
                self.fields['emergency_contact'].initial = customer.emergency_contact
            if 'planner' in self.fields:
                self.fields['planner'].initial = customer.planner
            if 'special_notes' in self.fields:
                self.fields['special_notes'].initial = customer.special_notes
    
    # CHANGED: Save customer fields when form is saved
    def save(self, commit=True):
        instance = super().save(commit=commit)
        # CHANGED: Only save customer if it was provided to the form
        if self._customer:
            self._customer.bride_name = self.cleaned_data.get('bride_name', '')
            self._customer.groom_name = self.cleaned_data.get('groom_name', '')
            self._customer.bride_contact = self.cleaned_data.get('bride_contact', '')
            self._customer.groom_contact = self.cleaned_data.get('groom_contact', '')
            self._customer.emergency_contact = self.cleaned_data.get('emergency_contact', '')
            self._customer.planner = self.cleaned_data.get('planner', '')
            self._customer.special_notes = self.cleaned_data.get('special_notes', '')
            if commit:
                self._customer.save()
        return instance