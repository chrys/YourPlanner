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
    # CHANGED: Added contact_number field
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact phone number for the professional"
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
    
    # CHANGED: Added bride and groom details
    bride_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Full name of the bride"
    )
    groom_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Full name of the groom"
    )
    bride_contact = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Bride contact phone number"
    )
    groom_contact = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Groom contact phone number"
    )
    emergency_contact = models.TextField(
        blank=True,
        null=True,
        help_text="Emergency contact name and phone number"
    )
    planner = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Wedding planner or coordinator name"
    )
    special_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Special notes for the wedding"
    )

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

    # CHANGED: Added method to get the active linked professional
    def get_linked_professional(self):
        """
        Get the active linked professional for this customer.
        
        Returns:
            Professional or None: The active linked professional, or None if not linked
        """
        try:
            link = ProfessionalCustomerLink.objects.select_related('professional').get(
                customer=self,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            )
            return link.professional
        except ProfessionalCustomerLink.DoesNotExist:
            return None

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


class Agent(TimeStampedModel):  # Agent user profile for order assignment
    """ Represents an Agent user profile linked to a User account. """
    
    class StatusChoices(models.TextChoices):  # Agent status options
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        SUSPENDED = 'SUSPENDED', 'Suspended'
    
    user = models.OneToOneField(  # Link to User
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='agent_profile'  # user.agent_profile
    )
    
    title = models.CharField(  # Agent title/role
        max_length=200,
        blank=True,
        null=True,
        help_text="Agent title or role (e.g., Support Agent, Sales Agent)"
    )
    
    bio = models.TextField(  # Agent bio/description
        blank=True,
        null=True,
        help_text="Brief bio or description of the agent"
    )
    
    department = models.CharField(  # Agent department
        max_length=200,
        blank=True,
        null=True,
        help_text="Department or team the agent belongs to"
    )
    
    status = models.CharField(  # Agent status
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        help_text="Current status of the agent"
    )
    
    profile_image = models.ImageField(  # Agent profile photo
        upload_to='agent_profiles/',
        null=True,
        blank=True,
        help_text="Agent profile photo"
    )
    
    contact_phone = models.CharField(  # Agent contact phone
        max_length=20,
        blank=True,
        null=True,
        help_text="Agent contact phone number"
    )
    
    notes = models.TextField(  # Admin notes about the agent
        blank=True,
        null=True,
        help_text="Internal notes about this agent"
    )
    
    labels = models.ManyToManyField(  # Labels for categorizing agents
        'labels.Label',
        blank=True,
        related_name='agents',
        help_text="Optional labels to categorize this agent"
    )
    
    # created_at and updated_at are inherited from TimeStampedModel

    def __str__(self):  # String representation
        return f"Agent: {self.title or self.user.get_full_name() or self.user.username}"
    
    def clean(self):  # Validation
        """Validate agent data."""
        # Add custom validation if needed
        pass
    
    def get_assigned_orders(self):  # Get all orders assigned to this agent
        """
        Get all orders assigned to this agent.
        
        Returns:
            QuerySet: All orders assigned to this agent
        """
        from orders.models import Order  # Import here to avoid circular imports
        return Order.objects.filter(assigned_agent=self)
    
    def get_active_orders(self):  # Get only pending/in-progress orders
        """
        Get all active (non-completed) orders assigned to this agent.
        
        Returns:
            QuerySet: Active orders assigned to this agent
        """
        from orders.models import Order  # Import here to avoid circular imports
        return Order.objects.filter(
            assigned_agent=self,
            status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS']
        )

    class Meta:  # Meta options
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['department']),
        ]
        permissions = [  # Custom permissions (only for creation/editing by admins)
            ('can_create_agent', 'Can create agent'),
            ('can_edit_agent', 'Can edit agent'),
            ('can_delete_agent', 'Can delete agent'),
        ]


class WeddingTimeline(TimeStampedModel):
    """
    CHANGED: Wedding Timeline model for storing wedding planning details.
    Stores event details, bride/groom information, and guest numbers.
    """
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='wedding_timeline'
    )
    
    # Event Details Section
    event_organiser_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Name of the event organiser"
    )
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Event organiser contact number"
    )
    pre_wedding_appointment = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time of pre-wedding appointment"
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Wedding venue location"
    )
    apostille_stamp = models.BooleanField(
        default=False,
        help_text="Whether apostille stamp is required"
    )
    ceremony_admin = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Name of ceremony administrator"
    )
    
    # Guest Numbers Section
    adults = models.IntegerField(
        default=0,
        help_text="Number of adult guests"
    )
    children = models.IntegerField(
        default=0,
        help_text="Number of children guests"
    )
    babies = models.IntegerField(
        default=0,
        help_text="Number of baby guests"
    )
    
    def __str__(self):
        return f"Wedding Timeline for {self.customer.user.get_full_name() or self.customer.user.username}"
    
    @property
    def total_guests(self):
        """Computed property for total guests."""
        return self.adults + self.children + self.babies
    
    class Meta:
        verbose_name = "Wedding Timeline"
        verbose_name_plural = "Wedding Timelines"