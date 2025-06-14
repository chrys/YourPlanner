from django import forms
from .models import Order, OrderItem
from services.models import Price # Corrected import for Price model
from django.conf import settings
from labels.models import Label
from users.models import ProfessionalCustomerLink 

class OrderForm(forms.ModelForm):
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        help_text="Optional labels to categorize this order"
    )
    
    class Meta:
        model = Order
        fields = []  # Empty list - no fields needed for initial order creation
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Remove labels field if user is a customer
        if self.user and hasattr(self.user, 'customer_profile'):
            if 'labels' in self.fields:
                del self.fields['labels']

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
    price_amount_at_order = forms.DecimalField(
        label="Price per Unit",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Custom Labels for this Item"
    )

    class Meta:
        model = OrderItem
        fields = []  # Empty list - no fields needed for initial order creation


    def __init__(self, *args, **kwargs):
        self.order_instance = kwargs.pop('order_instance', None)
        self.user = kwargs.pop('user', None)
        available_prices_queryset = kwargs.pop('available_prices_queryset', None)

        super().__init__(*args, **kwargs)

        self.fields['quantity'].widget.attrs.update({'class': 'form-control', 'min': '1'})
        if 'price' in self.fields:
            self.fields['price'].widget.attrs.update({'class': 'form-select'})

        if self.instance and self.instance.pk:  # This is an UPDATE form
            # Price (ForeignKey to services.Price) should always be read-only on update
            if 'price' in self.fields:
                price_field = self.fields['price']
                current_price_pk = self.instance.price.pk if self.instance.price else None
                if current_price_pk:
                    price_field.queryset = Price.objects.filter(pk=current_price_pk)
                else:
                    price_field.queryset = Price.objects.none()
                price_field.disabled = True
                price_field.help_text = "The underlying catalog item/price. Cannot be changed here."

            # price_amount_at_order field handling
            price_amount_field = self.fields['price_amount_at_order']
            can_edit_price = False # Default to not editable

            if self.user and hasattr(self.user, 'professional_profile') and self.user.professional_profile and self.order_instance:
                professional = self.user.professional_profile
                order_customer = self.order_instance.customer
                
                # Check if an active link exists between this professional and the order's customer
                is_linked_and_active = ProfessionalCustomerLink.objects.filter(
                    professional=professional,
                    customer=order_customer,
                    status=ProfessionalCustomerLink.StatusChoices.ACTIVE
                ).exists()
                
                if is_linked_and_active:
                    can_edit_price = True

            if can_edit_price:
                price_amount_field.disabled = False
                price_amount_field.help_text = "As a linked professional, you can override the price for this order item."
            else:
                price_amount_field.disabled = True
                price_amount_field.help_text = "Price per unit (read-only unless you are an actively linked professional for this customer)."
            
            self.initial['price_amount_at_order'] = self.instance.price_amount_at_order

            if self.instance.price and self.instance.price.item:
                self.fields['quantity'].label = f"Quantity for: {self.instance.price.item.title}"
            else:
                self.fields['quantity'].label = "Quantity"
            
        else:  # This is a CREATE form
            if 'price' in self.fields:
                if available_prices_queryset is not None:
                    self.fields['price'].queryset = available_prices_queryset
                else:
                     self.fields['price'].queryset = Price.objects.filter(is_active=True).select_related('item', 'item__service')
                self.fields['price'].empty_label = "Select an item/price"
            
            self.fields['price_amount_at_order'].disabled = False
            self.fields['price_amount_at_order'].help_text = "Price will be copied from selected item, or can be set manually if applicable."

        self.order_instance = kwargs.pop('order_instance', None)
        self.user = kwargs.pop('user', None)
        available_prices_queryset = kwargs.pop('available_prices_queryset', None)

        super().__init__(*args, **kwargs)

        self.fields['quantity'].widget.attrs.update({'class': 'form-control', 'min': '1'})
        if 'price' in self.fields:
            self.fields['price'].widget.attrs.update({'class': 'form-select'})

        if self.instance and self.instance.pk:  # This is an UPDATE form
            # Price (ForeignKey to services.Price) should always be read-only on update
            if 'price' in self.fields:
                price_field = self.fields['price']
                current_price_pk = self.instance.price.pk if self.instance.price else None
                if current_price_pk:
                    price_field.queryset = Price.objects.filter(pk=current_price_pk)
                else:
                    price_field.queryset = Price.objects.none()
                price_field.disabled = True
                price_field.help_text = "The underlying catalog item/price."

            # price_amount_at_order field handling
            price_amount_field = self.fields['price_amount_at_order']
            can_edit_price = False # Default to not editable

            if self.user and hasattr(self.user, 'professional_profile') and self.user.professional_profile and self.order_instance:
                professional = self.user.professional_profile
                order_customer = self.order_instance.customer
                
                # Check if an active link exists between this professional and the order's customer
                is_linked_and_active = ProfessionalCustomerLink.objects.filter(
                    professional=professional,
                    customer=order_customer,
                    status=ProfessionalCustomerLink.StatusChoices.ACTIVE
                ).exists()
                
                if is_linked_and_active:
                    can_edit_price = True

            can_edit_price = True #TODO temporary until this bug is fixed
            if can_edit_price:
                price_amount_field.disabled = False
                price_amount_field.help_text = "Price per unit"
            else:
                price_amount_field.disabled = True
                price_amount_field.help_text = "Price per unit"
            
            self.initial['price_amount_at_order'] = self.instance.price_amount_at_order

            if self.instance.price and self.instance.price.item:
                self.fields['quantity'].label = f"Quantity for: {self.instance.price.item.title}"
            else:
                self.fields['quantity'].label = "Quantity"
            
        else:  # This is a CREATE form
            if 'price' in self.fields:
                if available_prices_queryset is not None:
                    self.fields['price'].queryset = available_prices_queryset
                else:
                     self.fields['price'].queryset = Price.objects.filter(is_active=True).select_related('item', 'item__service')
                self.fields['price'].empty_label = "Select an item/price"
            
            self.fields['price_amount_at_order'].disabled = False
            self.fields['price_amount_at_order'].help_text = "Price will be copied from selected item, or can be set manually if applicable."