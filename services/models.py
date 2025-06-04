from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel, ActiveManager
from django.utils.text import slugify

class ServiceCategory(TimeStampedModel):
    """
    Categories for organizing services.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, help_text="Optional description of this category")
    slug = models.SlugField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ['name']


class Service(TimeStampedModel):
    """ A service offered by a Professional. """
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
    is_active = models.BooleanField(default=True, help_text="Is this service currently offered?")
    featured = models.BooleanField(default=False, help_text="Feature this service in listings?")
    slug = models.SlugField(max_length=255, blank=True)
    # created_at and updated_at are inherited from TimeStampedModel
    
    # Add custom managers
    objects = models.Manager()  # The default manager
    active = ActiveManager()  # Custom manager for active services only

    def __str__(self):
        return f"{self.title} (by {self.professional})"
    
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
    def calculate_average_rating(self):
        """
        Calculate the average rating for this service from reviews.
        """
        # This is a placeholder - would need a Review model to implement fully
        return 0.0

    class Meta:
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
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE, # If service deleted, delete its items
        related_name='items' # service.items.all()
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='item_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text="Is this item currently available?")

    sku = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Stock Keeping Unit - unique identifier for this item"
    )
    stock = models.PositiveIntegerField(
        default=0,
        help_text="Number of items in stock (0 for unlimited or not applicable)"
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text="Position of this item in the service display"
    )
    slug = models.SlugField(max_length=255, blank=True)
    # created_at and updated_at are inherited from TimeStampedModel
    
    # Add custom managers
    objects = models.Manager()  # The default manager
    
    def __str__(self):
        return f"{self.title} (in Service: {self.service.title})"
    
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
    
    def is_available(self):
        """
        Check if this item is available based on stock.
        """
        # If stock is 0, it means unlimited or not applicable
        return self.stock > 0 or self.stock == 0

    class Meta:
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
    # created_at and updated_at are inherited from TimeStampedModel
    
    # Add custom managers
    objects = models.Manager()  # The default manager
    active = ActiveManager()  # Custom manager for active prices only

    def __str__(self):
        return f"{self.amount} {self.currency} ({self.frequency}) for {self.item.title}"
    
    def clean(self):
        """
        Validate the price data.
        """
        if self.amount < 0:
            raise ValidationError({'amount': 'Price amount cannot be negative'})
        
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            raise ValidationError({'valid_until': 'End date must be after start date'})
        
        if self.min_quantity < 1:
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

    class Meta:
        verbose_name = "Price"
        verbose_name_plural = "Prices"
        ordering = ['item', 'amount']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['valid_from', 'valid_until']),
        ]
