from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel, ActiveManager


class Template(TimeStampedModel):
    """
    A template is a collection of Services that can be offered to Customers.
    """
    professional = models.ForeignKey(
        'users.Professional',
        on_delete=models.CASCADE,
        related_name='templates'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, help_text="Is this template currently available?")
    slug = models.SlugField(max_length=255, blank=True)
    
    # Add custom managers
    objects = models.Manager()  # The default manager
    active = ActiveManager()  # Custom manager for active templates only
    
    def __str__(self):
        return f"{self.title} (by {self.professional})"
    
    def save(self, *args, **kwargs):
        if not hasattr(self, 'professional') or self.professional is None:
            raise ValidationError("Template must have a professional.")
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.professional.pk}")
        super().save(*args, **kwargs)
    
    def clean(self):
        """
        Validate the template data.
        """
        if not self.title:
            raise ValidationError({'title': 'Template title cannot be empty'})
        
        # Check for duplicate titles for the same professional
        if Template.objects.filter(
            professional=self.professional, 
            title=self.title
        ).exclude(pk=self.pk).exists():
            raise ValidationError({'title': 'You already have a template with this title'})
    
    class Meta:
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        ordering = ['professional', 'title']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['professional', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['professional', 'slug'],
                name='unique_professional_template_slug'
            )
        ]


class TemplateImage(TimeStampedModel):
    """
    Images associated with a Template.
    """
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='template_images/')
    is_default = models.BooleanField(default=False, help_text="Is this the default image for the template?")
    alt_text = models.CharField(max_length=255, blank=True, help_text="Alternative text for the image")
    position = models.PositiveIntegerField(default=0, help_text="Position of this image in the template display")
    
    def __str__(self):
        default_status = " (Default)" if self.is_default else ""
        return f"Image for {self.template.title}{default_status}"
    
    def save(self, *args, **kwargs):
        # If this image is being set as default, unset any other default images
        if self.is_default:
            TemplateImage.objects.filter(
                template=self.template, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        # If this is the first image for the template, make it the default
        if not self.pk and not TemplateImage.objects.filter(template=self.template).exists():
            self.is_default = True
            
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Template Image"
        verbose_name_plural = "Template Images"
        ordering = ['template', 'position']
        indexes = [
            models.Index(fields=['template', 'position']),
            models.Index(fields=['is_default']),
        ]


class TemplateService(TimeStampedModel):
    """
    Association between a Template and a Service.
    """
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name='template_services'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='template_services'
    )
    position = models.PositiveIntegerField(default=0, help_text="Position of this service in the template")
    
    def __str__(self):
        return f"{self.service.title} in {self.template.title}"
    
    def clean(self):
        """
        Validate the template service data.
        """
        # Ensure the service belongs to the same professional as the template
        if self.template.professional != self.service.professional:
            raise ValidationError({
                'service': 'Service must belong to the same professional as the template'
            })
    
    class Meta:
        verbose_name = "Template Service"
        verbose_name_plural = "Template Services"
        ordering = ['template', 'position']
        indexes = [
            models.Index(fields=['template', 'position']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['template', 'service'],
                name='unique_template_service'
            )
        ]

