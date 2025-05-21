from django import forms
from .models import Service, Item, Price

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'is_active']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'image']

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['amount', 'currency', 'frequency']
        labels = {
            'amount': 'Price',
            'currency': 'Currency',
            'frequency': 'Frequency',
        }