from django import forms
from .models import Service, Item, Price

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ItemForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}), help_text="Upload an image for the item (optional).", required=False)
    class Meta:
        model = Item
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['amount', 'currency', 'frequency', 'description', 'is_active']
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