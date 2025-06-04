from django import forms
from .models import Order, OrderItem
from services.models import Price # Corrected import for Price model
from django.conf import settings
from labels.models import Label

class OrderForm(forms.ModelForm):
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text="Optional labels to categorize this order"
    )
    
    class Meta:
        model = Order
        fields = ['labels'] # Added labels field

class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) # User passed from view for dynamic choices
        super().__init__(*args, **kwargs)
        # TODO: Implement dynamic status choices based on user role and current order status
        # For example:
        # if user and not user.is_staff:
        #     # Limit choices for non-staff
        #     self.fields['status'].choices = [
        #         (Order.StatusChoices.PENDING, Order.StatusChoices.PENDING.label),
        #         (Order.StatusChoices.CANCELLED, Order.StatusChoices.CANCELLED.label),
        #     ]
        # elif self.instance and self.instance.pk:
        #     # Limit choices based on current status for staff
        #     # e.g., cannot go from COMPLETED back to PENDING easily
        #     pass


class OrderItemForm(forms.ModelForm):
    # Price will be dynamically set up in __init__
    price = forms.ModelChoiceField(queryset=Price.objects.none(), widget=forms.Select(attrs={'class': 'form-select'}))
    quantity = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}), initial=1)
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text="Optional labels to categorize this order item"
    )

    class Meta:
        model = OrderItem
        fields = ['price', 'quantity', 'labels']

    def __init__(self, *args, **kwargs):
        order_instance = kwargs.pop('order_instance', None)
        available_prices_queryset = kwargs.pop('available_prices_queryset', None)
        super().__init__(*args, **kwargs)

        if available_prices_queryset is not None:
            self.fields['price'].queryset = available_prices_queryset
        elif self.instance and self.instance.pk and self.instance.price:
            # If updating and a price is already set, limit queryset to that price
            # and disable the field.
             self.fields['price'].queryset = Price.objects.filter(pk=self.instance.price.pk)
             self.fields['price'].initial = self.instance.price
             self.fields['price'].disabled = True # Disable price selection during update
        else:
            # Fallback, should ideally always get a queryset from the view for new items
            self.fields['price'].queryset = Price.objects.none()

        # If instance exists (updating), quantity can be set from instance
        if self.instance and self.instance.pk:
            self.fields['quantity'].initial = self.instance.quantity

        # Further customization, e.g. help text for price field to show item/service
        if self.fields['price'].queryset:
            self.fields['price'].label_from_instance = lambda obj: f"{obj.item.service.title} - {obj.item.title} (${obj.amount} {obj.currency} / {obj.get_frequency_display})"


    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')

        if self.instance and self.instance.pk and self.fields['price'].disabled:
            # If the price field was disabled (for an existing OrderItem),
            # ensure we use the existing price instance rather than trying to
            # validate it from potentially empty queryset.
            cleaned_data['price'] = self.instance.price

        return cleaned_data
