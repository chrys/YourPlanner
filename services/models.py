from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ValidationError

class Service(models.Model):
    """ A service offered by a Professional. """
    professional = models.ForeignKey(
        'users.Professional', # Use string notation for cross-app relations
        on_delete=models.CASCADE, # If professional deleted, delete their services
        related_name='services' # professional.services.all()
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, help_text="Is this service currently offered?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (by {self.professional})"

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['professional', 'title']


class Item(models.Model):
    """ An individual item or component within a Service. """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE, # If service deleted, delete its items
        related_name='items' # service.items.all()
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        
    def __str__(self):
        return f"{self.title} (in Service: {self.service.title})"

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ['service', 'title']


class Price(models.Model):
    """ Represents a price point for a specific Item. """
    class FrequencyChoices(models.TextChoices):
        ONE_TIME = 'ONCE', 'One-Time'
        HOURLY = 'HOURLY', 'Hourly'
        DAILY = 'DAILY', 'Daily'
        WEEKLY = 'WEEKLY', 'Weekly'
        MONTHLY = 'MONTHLY', 'Monthly'
        ANNUALLY = 'ANNUALLY', 'Annually'
        # Add other frequencies as needed

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE, # If item deleted, delete its prices
        related_name='prices' # item.prices.all()
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD') # Consider choices or separate model
    frequency = models.CharField(
        max_length=10,
        choices=FrequencyChoices.choices,
        default=FrequencyChoices.ONE_TIME
    )
    description = models.CharField(max_length=255, blank=True, help_text="Optional description (e.g., 'Standard Tier', 'Discounted')")
    is_active = models.BooleanField(default=True, help_text="Is this price option currently available?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.amount} {self.currency} ({self.frequency}) for {self.item.title}"

    class Meta:
        verbose_name = "Price"
        verbose_name_plural = "Prices"
        ordering = ['item', 'amount']
