from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel
from django.core.exceptions import ValidationError


# No separate User model here - we link to settings.AUTH_USER_MODEL
# If you needed custom fields ON the User model itself (not profile),
# you would create a Custom User Model inheriting from AbstractUser.

class Professional(TimeStampedModel):
    """ Represents a Professional user profile linked to a User account. """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True, # Use the user's ID as the primary key
        related_name='professional_profile' # user.professional_profile
    )
    title = models.CharField(max_length=200, blank=True, null=True)  # <-- Add this line
    specialization = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    default = models.BooleanField(
        default=False,
        help_text="If True, this professional will be used as the default for new orders"
    )
    profile_image = models.ImageField(
        upload_to='professional_profiles/',
        null=True,
        blank=True,
        help_text="Professional profile photo"
    )
    contact_hours = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Hours when the professional is available for contact"
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average rating from customers (1.00-5.00)"
    )
    labels = models.ManyToManyField(
        'labels.Label',
        blank=True,
        related_name='professionals',
        help_text="Optional labels to categorize this professional"
    )
    # created_at and updated_at are inherited from TimeStampedModel

    def __str__(self):
        # Access the related user's identifier (e.g., username or email)
        return self.title or self.user.get_full_name() or self.user.username  # Show title if available, else fallback
    
    def clean(self):
        """
        Validate professional data.
        """
        if self.rating and (self.rating < 1 or self.rating > 5):
            raise ValidationError({'rating': 'Rating must be between 1 and 5'})
        
        # Ensure only one default professional exists
        if self.default:
            default_exists = Professional.objects.filter(default=True).exclude(pk=self.pk).exists()
            if default_exists:
                raise ValidationError({'default': 'There can only be one default professional'})
    
    def calculate_availability(self, date=None):
        """
        Calculate availability for scheduling on a given date.
        If no date is provided, returns availability for the current date.
        """
        # This is a placeholder - would need a scheduling system to implement fully
        return []

    class Meta:
        verbose_name = "Professional"
        verbose_name_plural = "Professionals"
        indexes = [
            models.Index(fields=['rating']),
        ]

class Customer(TimeStampedModel):
    """ Represents a Customer user profile linked to a User account. """
    
    # Add RoleChoices class for customer roles
    class RoleChoices(models.TextChoices):
        STANDARD = 'STANDARD', 'Standard'
        PREMIUM = 'PREMIUM', 'Premium'
        VIP = 'VIP', 'VIP'
        ENTERPRISE = 'ENTERPRISE', 'Enterprise'
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True, # Use the user's ID as the primary key
        related_name='customer_profile' # user.customer_profile
    )
    company_name = models.CharField(max_length=200, blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True, help_text="Default shipping address")
    billing_address = models.TextField(blank=True, null=True, help_text="Default billing address")
    preferred_currency = models.CharField(max_length=3, default='EUR', blank=True, help_text="Preferred currency for pricing")
    marketing_preferences = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Marketing communication preferences"
    )
    wedding_day = models.DateField(help_text="The planned wedding day (must be in the future).")

    # New role field - not accessible by customers
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.STANDARD,
        help_text="Customer role - determines access levels and features"
    )
    labels = models.ManyToManyField(
        'labels.Label',
        blank=True,
        related_name='customers',
        help_text="Optional labels to categorize this customer"
    )
    # created_at and updated_at are inherited from TimeStampedModel

    def __str__(self):
        return f"Customer: {self.user}"
    
    def clean(self):
        """
        Validate customer data.
        """
        if self.preferred_currency and len(self.preferred_currency) != 3:
            raise ValidationError({'preferred_currency': 'Currency code must be 3 characters'})
    
        if self.wedding_day and self.wedding_day <= timezone.now().date():
            raise ValidationError({'wedding_day': 'The wedding day must be in the future.'})
        
    def calculate_lifetime_value(self):
        """
        Calculate the customer's lifetime value based on their orders.
        """
        from django.db.models import Sum
        
        # Get the total amount of all completed orders
        total = self.orders.filter(
            status='COMPLETED'
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        return total

    def has_role(self, role_name):
        """
        Check if the customer has a specific role.
        
        Args:
            role_name (str): The role name to check (e.g., 'PREMIUM', 'VIP')
            
        Returns:
            bool: True if the customer has the specified role, False otherwise
        """
        return self.role == role_name
    
    def has_minimum_role(self, role_name):
        """
        Check if the customer has at least the specified role level.
        Roles are ordered: STANDARD < PREMIUM < VIP < ENTERPRISE
        
        Args:
            role_name (str): The minimum role level to check
            
        Returns:
            bool: True if the customer has at least the specified role level, False otherwise
        """
        role_levels = {
            self.RoleChoices.STANDARD: 0,
            self.RoleChoices.PREMIUM: 1,
            self.RoleChoices.VIP: 2,
            self.RoleChoices.ENTERPRISE: 3
        }
        
        customer_level = role_levels.get(self.role, 0)
        required_level = role_levels.get(role_name, 0)
        
        return customer_level >= required_level

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        indexes = [
            models.Index(fields=['company_name']),
        ]

class ProfessionalCustomerLink(TimeStampedModel):
    """ Represents a link or relationship between a Professional and a Customer. """
    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        REQUESTED = 'REQUESTED', 'Requested'
        # Add other statuses as needed
    
    class CommunicationPreference(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        PHONE = 'PHONE', 'Phone'
        SMS = 'SMS', 'SMS'
        APP = 'APP', 'In-App'
        ANY = 'ANY', 'Any Method'

    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='customer_links' # professional.customer_links.all()
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='professional_links' # customer.professional_links.all()
    )
    relationship_start_date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Notes about this professional-customer relationship"
    )
    last_interaction_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date of the last interaction between professional and customer"
    )
    preferred_communication = models.CharField(
        max_length=10,
        choices=CommunicationPreference.choices,
        default=CommunicationPreference.EMAIL,
        help_text="Preferred method of communication"
    )
    # created_at is inherited from TimeStampedModel

    def __str__(self):
        return f"Link: {self.professional} <-> {self.customer} ({self.status})"
    
    def calculate_relationship_duration(self):
        """
        Calculate the duration of the relationship in days.
        """
        from django.utils import timezone
        return (timezone.now().date() - self.relationship_start_date).days

    class Meta:
        verbose_name = "Professional-Customer Link"
        verbose_name_plural = "Professional-Customer Links"
        # Ensure a professional and customer can only be linked once
        constraints = [
            models.UniqueConstraint(
                fields=['professional', 'customer'],
                name='unique_professional_customer_link'
            )
        ]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['relationship_start_date']),
            models.Index(fields=['last_interaction_date']),
        ]
