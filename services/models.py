from django.db import models
from django.db.models import DecimalField, ImageField, IntegerField, QuerySet
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel, ActiveManager
from django.utils.text import slugify
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.models import Price as PriceModel
    

class PriceQuerySet(models.QuerySet):
    # CHANGED: Moved PriceQuerySet before Item class for proper ordering
    """Custom QuerySet for Price model with filtering methods."""
    def for_item(self, item):
        """Return prices for a specific item."""
        return self.filter(item=item)
    
    def active(self):
        """Return only active prices."""
        return self.filter(is_active=True)
    
    def valid_now(self):
        """Return prices that are currently valid based on date range."""
        from django.utils import timezone
        now = timezone.now()
        return self.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__isnull=True
        ) | self.filter(
            is_active=True,
            valid_from__isnull=True,
            valid_until__gte=now
        ) | self.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )


class ServiceQuerySet(models.QuerySet):
    def owned_by(self, professional):
        """Return services owned by the given professional."""
        return self.filter(professional=professional)  #moved repeated query here

    def active(self):
        """Return only active services."""
        return self.filter(is_active=True)  #moved repeated query here
    
class ServiceCategory(TimeStampedModel):
    """
    Categories for organizing services.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(
        blank=True, 
        null=True, 
        default=None,
        help_text="Optional description of this category")
    slug = models.SlugField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta(TimeStampedModel.Meta):  # CHANGED: Explicitly inherit from parent Meta
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ['name']


class Service(TimeStampedModel):
    """ A service offered by a Professional. """
    objects = ServiceQuerySet.as_manager()  # use custom manager
    active = ActiveManager()  # Custom manager for active services only
    professional = models.ForeignKey(
        'users.Professional', # Use string notation for cross-app relations
        on_delete=models.CASCADE, # If professional deleted, delete their services
        related_name='services' # professional.services.all()
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = ImageField(upload_to='service_images/', null=True, blank=True)

    is_active = models.BooleanField(default=True, help_text="Is this service currently offered?")
    featured = models.BooleanField(default=False, help_text="Feature this service in listings?")
    slug = models.SlugField(max_length=255, blank=True)
    labels = models.ManyToManyField(
        'labels.Label',
        blank=True,
        related_name='services',
        help_text="Optional labels to categorize this service"
    )
    # created_at and updated_at are inherited from TimeStampedModel
    

    def __str__(self):
        return f"{self.title} (by {self.professional})"
    
    # CHANGED: Added method to get service-level prices
    def get_service_prices(self):
        """Return all active prices directly linked to this service."""
        return self.prices.filter(is_active=True).order_by('amount')
    
    # CHANGED: Added method to get active prices (service or items)
    def get_all_prices(self):
        """Return all active prices (both service-level and item-level)."""
        # CHANGED: Fixed to avoid ORDER BY in union queries
        service_prices = list(self.prices.filter(is_active=True))
        item_prices = list(Price.objects.filter(item__service=self, is_active=True))
        all_prices = service_prices + item_prices
        return sorted(all_prices, key=lambda p: (p.amount, p.created_at))
    
    def save(self, *args, **kwargs):
        if not hasattr(self, 'professional') or self.professional is None:
            raise ValidationError("Service must have a professional.")
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.professional.pk}")
        super().save(*args, **kwargs)
    
    def clean(self):
        """
        Validate the service data.
        """
        if not self.title:
            raise ValidationError({'title': 'Service title cannot be empty'})
        
        # Only check for duplicate titles if we have a professional
        if hasattr(self, 'professional') and self.professional:
            # Check for duplicate titles for the same professional
            if Service.objects.filter(
                professional=self.professional, 
                title=self.title
            ).exclude(pk=self.pk).exists():
                raise ValidationError({'title': 'You already have a service with this title'})

    class Meta(TimeStampedModel.Meta):  # CHANGED: Explicitly inherit from parent Meta
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['professional', 'title']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['featured']),
            models.Index(fields=['professional', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['professional', 'slug'],
                name='unique_professional_service_slug'
            )
        ]


class Item(TimeStampedModel):
    """ An individual item or component within a Service. """
    prices: 'PriceQuerySet'  # type: ignore
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE, # If service deleted, delete its items
        related_name='items' # service.items.all()
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='item_images/', null=True, blank=True)
    quantity = IntegerField(default=0, validators=[MinValueValidator(0)], help_text="Available quantity, cannot be negative.")
    min_quantity = IntegerField(null=True, blank=True, validators=[MinValueValidator(1)], help_text="Minimum quantity per order.")
    max_quantity = IntegerField(null=True, blank=True, validators=[MinValueValidator(1)], help_text="Maximum quantity per order.")
    is_active = models.BooleanField(default=True, help_text="Is this item currently available?")

    sku = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Stock Keeping Unit - unique identifier for this item"
    )
    stock = models.PositiveIntegerField( # This field might become redundant or be used differently with quantity
        default=0,
        help_text="Number of items in stock (0 for unlimited or not applicable)"
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text="Position of this item in the service display"
    )
    slug = models.SlugField(max_length=255, blank=True)
    labels = models.ManyToManyField(
        'labels.Label',
        blank=True,
        related_name='items',
        help_text="Optional labels to categorize this item"
    )
    # created_at and updated_at are inherited from TimeStampedModel
    
    # Add custom managers
    objects = models.Manager()  # The default manager
    
    def __str__(self):
        return f"{self.title} (in Service: {self.service.title})"
    
    def get_active_prices(self):
        # Added method to get active prices for this item
        """Return all active prices for this item."""
        return self.prices.filter(is_active=True).order_by('amount')
    
    def get_valid_prices(self):
        # Added method to get currently valid prices (date-aware)
        """Return prices that are currently valid based on date range."""
        return self.prices.valid_now()
    
    def get_price_for_quantity(self, quantity):
        # CHANGED: Added method to find applicable price for a quantity
        """Find the best price for a given quantity."""
        return self.prices.active().filter(
            min_quantity__lte=quantity
        ).filter(
            models.Q(max_quantity__isnull=True) | models.Q(max_quantity__gte=quantity)
        ).order_by('-min_quantity').first()
    
    def save(self, *args, **kwargs):
        if not hasattr(self, 'service') or self.service is None:
            raise ValidationError("Item must have a service.")
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.service.pk}")
        super().save(*args, **kwargs)
    
    def clean(self):
        """
        Validate the item data.
        """
        if not self.title:
            raise ValidationError({'title': 'Item title cannot be empty'})

        if self.min_quantity is not None and self.max_quantity is not None:
            if self.max_quantity < self.min_quantity:
                raise ValidationError({'max_quantity': 'Maximum quantity cannot be less than minimum quantity.'})
    
    def is_available(self):
        """
        Check if this item is available based on stock.
        """
        # If stock is 0, it means unlimited or not applicable
        return self.stock > 0 or self.stock == 0

    class Meta(TimeStampedModel.Meta):  # CHANGED: Explicitly inherit from parent Meta
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ['service', 'position', 'title']
        indexes = [
            models.Index(fields=['service', 'position']),
            models.Index(fields=['sku']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'slug'],
                name='unique_service_item_slug'
            )
        ]





class Price(TimeStampedModel):
    """ Represents a price point for a specific Item or Service. """
    # CHANGED: Updated docstring to reflect service pricing support
    class FrequencyChoices(models.TextChoices):
        ONE_TIME = 'ONCE', 'One-Time'
        HOURLY = 'HOURLY', 'Hourly'
        DAILY = 'DAILY', 'Daily'
        WEEKLY = 'WEEKLY', 'Weekly'
        MONTHLY = 'MONTHLY', 'Monthly'
        ANNUALLY = 'ANNUALLY', 'Annually'
        # Add other frequencies as needed

    # CHANGED: Make item optional to support service-level pricing
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='prices',
        null=True,  # CHANGED: Now optional to support service-level pricing
        blank=True  # CHANGED: Now optional
    )
    # CHANGED: Added optional service relationship for direct service pricing
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='prices',
        null=True,
        blank=True,
        help_text="Optional: Link price directly to service (bypasses item level)"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    CURRENCY_CHOICES = [
        ('EUR', 'Euro'),
        ('USD', 'US Dollar'),
        ('GBP', 'British Pound'),
    ]
    currency = models.CharField(
        max_length=3, 
        choices=CURRENCY_CHOICES,
        default='EUR', 
        blank=True
    ) 
    frequency = models.CharField(
        max_length=10,
        choices=FrequencyChoices.choices,
        default=FrequencyChoices.ONE_TIME
    )
    description = models.CharField(max_length=255, blank=True, help_text="Optional description (e.g., 'Standard Tier', 'Discounted')")
    is_active = models.BooleanField(default=True, help_text="Is this price option currently available?")
    valid_from = models.DateTimeField(null=True, blank=True, help_text="When this price becomes valid")
    valid_until = models.DateTimeField(null=True, blank=True, help_text="When this price expires")
    min_quantity = models.PositiveIntegerField(default=1, help_text="Minimum quantity for this price")
    max_quantity = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum quantity for this price (blank for unlimited)")
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Discount percentage applied to this price"
    )
    labels = models.ManyToManyField(
        'labels.Label',
        blank=True,
        related_name='prices',
        help_text="Optional labels to categorize this price"
    )
    # created_at and updated_at are inherited from TimeStampedModel
    
    # Use custom manager with queryset
    objects = PriceQuerySet.as_manager()
    active = ActiveManager()  # Custom manager for active prices only

    # CHANGED: Updated __str__ to handle both service and item pricing
    def __str__(self):
        if self.service:
            return f"{self.amount} {self.currency} ({self.frequency}) for Service: {self.service.title}"
        elif self.item:
            return f"{self.amount} {self.currency} ({self.frequency}) for {self.item.title}"
        return f"{self.amount} {self.currency} ({self.frequency})"
    
    def clean(self):
        """
        Validate the price data.
        CHANGED: Added validation that price must link to item OR service, not both or neither
        """
        # CHANGED: Only prevent linking to BOTH item and service at the same time
        # Allow None for either one (will be set by the view)
        if self.item and self.service:
            raise ValidationError("Price cannot be linked to both an Item and a Service. Choose one.")
        
        if self.amount and self.amount < 0:
            raise ValidationError({'amount': 'Price amount cannot be negative'})
        
        # CHANGED: Check if both dates exist before comparing
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            raise ValidationError({'valid_until': 'End date must be after start date'})
        
        if self.min_quantity and self.min_quantity < 1:
            raise ValidationError({'min_quantity': 'Minimum quantity must be at least 1'})
        
        if self.max_quantity and self.min_quantity > self.max_quantity:
            raise ValidationError({'max_quantity': 'Maximum quantity must be greater than minimum quantity'})
    
    def is_valid_now(self):
        """
        Check if this price is currently valid based on date range.
        """
        from django.utils import timezone
        now = timezone.now()
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        return self.is_active
    
    def get_discounted_amount(self):
        """
        Calculate the discounted price amount.
        """
        if self.discount_percentage > 0:
            discount = (self.amount * self.discount_percentage) / Decimal('100.00')
            return self.amount - discount
        return self.amount

    class Meta(TimeStampedModel.Meta):  # CHANGED: Explicitly inherit from parent Meta
        verbose_name = "Price"
        verbose_name_plural = "Prices"
        # CHANGED: Updated ordering to handle both item and service prices
        ordering = ['amount']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['valid_from', 'valid_until']),
            models.Index(fields=['item']),  # CHANGED: Added index for item queries
            models.Index(fields=['service']),  # CHANGED: Added index for service queries
        ]
        


