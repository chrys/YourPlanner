from django import forms
from .models import Service, Item, Price
from labels.models import Label

class ServiceForm(forms.ModelForm):
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.filter(label_type='SERVICE'), # MODIFIED
        required=False,
        widget=forms.CheckboxSelectMultiple, # MODIFIED
        help_text="Optional labels to categorize this service"
    )
    
    class Meta:
        model = Service
        fields = ['title', 'description', 'is_active', 'labels']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Note: widget for labels is now part of the field definition above
        }

class ItemForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}), help_text="Upload an image for the item (optional).", required=False)
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.filter(label_type='ITEM'), # MODIFIED
        required=False,
        widget=forms.CheckboxSelectMultiple, # MODIFIED
        help_text="Optional labels to categorize this item"
    )
    
    class Meta:
        model = Item
        fields = ['title', 'description', 'image', 'labels']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # Note: widget for labels is now part of the field definition above
        }

class PriceForm(forms.ModelForm):
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text="Optional labels to categorize this price"
    )
    
    class Meta:
        model = Price
        fields = ['amount', 'currency', 'frequency', 'description', 'is_active', 'labels']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'amount': 'Price',
            'currency': 'Currency',
            'frequency': 'Frequency',
            'is_active': 'Active',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use model's choices
        self.fields['currency'].choices = Price.CURRENCY_CHOICES
        # Set initial only if not editing an instance and not POST
        if not self.instance.pk and not self.data.get('currency'):
            self.initial['currency'] = 'EUR'
