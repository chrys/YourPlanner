from django.db import models
from core.models import TimeStampedModel

LABEL_TYPES = (
    ('professional', 'Professional Tag'),
    ('customer', 'Customer Tag'),
    ('service', 'Service Tag'),
    ('item', 'Item Tag'),
    ('price', 'Price Tag'),
    ('order', 'Order Tag'),
)

class Label(TimeStampedModel):
    """
    Represents a label that can be applied to various entities in the system.
    """
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=LABEL_TYPES, default='general')
    description = models.TextField(blank=True, null=True, help_text="Optional description of this label")
    color = models.CharField(max_length=7, default="#CCCCCC", help_text="Hex color code for the label")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Label"
        verbose_name_plural = "Labels"
        ordering = ['name']
