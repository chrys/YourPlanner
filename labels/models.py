from django.db import models
from core.models import TimeStampedModel

# Placeholder: Replace with your actual models
# from customers.models import Customer
# from professionals.models import Professional
# etc.
class CustomerPlaceholder: pass
class ProfessionalPlaceholder: pass
class ServicePlaceholder: pass
class ItemPlaceholder: pass
class PricePlaceholder: pass
class OrderPlaceholder: pass


LABEL_TYPES = (
    ('CUSTOMER', 'Customer'),
    ('PROFESSIONAL', 'Professional'),
    ('SERVICE', 'Service'),
    ('ITEM', 'Item'),
    ('PRICE', 'Price'),
    ('ORDER', 'Order'),
)

# This dictionary maps the string identifiers from LABEL_TYPES
# to the actual Django model classes.
LABEL_TYPES_ASSOCIATIONS = {
    'CUSTOMER': CustomerPlaceholder,
    'PROFESSIONAL': ProfessionalPlaceholder,
    'SERVICE': ServicePlaceholder,
    'ITEM': ItemPlaceholder,
    'PRICE': PricePlaceholder,
    'ORDER': OrderPlaceholder,
}

class Label(TimeStampedModel):
    """
    Represents a label that can be applied to various entities in the system.
    """
    name = models.CharField(max_length=100, unique=True)
    # Changed 'type' to 'label_type' to avoid conflict with Python's built-in type
    label_type = models.CharField(
        max_length=50, # Increased max_length to accommodate longer keys like 'PROFESSIONAL'
        choices=LABEL_TYPES,
        default='ITEM', # Added a default value
        db_index=True # Added db_index as it's likely to be queried often
    )
    description = models.TextField(blank=True, null=True, help_text="Optional description of this label")
    color = models.CharField(max_length=7, default="#CCCCCC", help_text="Hex color code for the label")
    
    def __str__(self):
        # Updated to use get_label_type_display for better readability
        return f"{self.name} ({self.get_label_type_display()})"
    
    class Meta:
        verbose_name = "Label"
        verbose_name_plural = "Labels"
        ordering = ['name']
