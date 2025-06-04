from django.db import models
from core.models import TimeStampedModel

class ConfigurationCategory(TimeStampedModel):
    """
    Categories for organizing configuration labels.
    """
    CATEGORY_CHOICES = [
        ('WEBSITE', 'Website'),
        ('PROFESSIONAL', 'Professional'),
        ('SERVICE', 'Services and Items'),
        ('CUSTOMER', 'Customer'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True, help_text="Description of this configuration category")
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        verbose_name = "Configuration Category"
        verbose_name_plural = "Configuration Categories"
        ordering = ['name']


class ConfigurationLabel(TimeStampedModel):
    """
    Labels for different entities that can be configured by admins.
    """
    category = models.ForeignKey(
        ConfigurationCategory,
        on_delete=models.CASCADE,
        related_name='labels'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, help_text="Explanation of this label")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    class Meta:
        verbose_name = "Configuration Label"
        verbose_name_plural = "Configuration Labels"
        ordering = ['category', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name'],
                name='unique_category_label'
            )
        ]

