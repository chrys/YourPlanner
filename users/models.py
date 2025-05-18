from django.db import models
from django.conf import settings
from django.utils import timezone

# No separate User model here - we link to settings.AUTH_USER_MODEL
# If you needed custom fields ON the User model itself (not profile),
# you would create a Custom User Model inheriting from AbstractUser.

class Professional(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Access the related user's identifier (e.g., username or email)
        return self.title or self.user.get_full_name() or self.user.username  # Show title if available, else fallback

    class Meta:
        verbose_name = "Professional"
        verbose_name_plural = "Professionals"


class Customer(models.Model):
    """ Represents a Customer user profile linked to a User account. """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True, # Use the user's ID as the primary key
        related_name='customer_profile' # user.customer_profile
    )
    company_name = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer: {self.user}"

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


class ProfessionalCustomerLink(models.Model):
    """ Represents a link or relationship between a Professional and a Customer. """
    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        REQUESTED = 'REQUESTED', 'Requested'
        # Add other statuses as needed

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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Link: {self.professional} <-> {self.customer} ({self.status})"

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