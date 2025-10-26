from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from users.models import Professional 
from services.models import Service, Item  # Added Item import
from decimal import Decimal 
from django.core.validators import MinValueValidator 

class Template(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='templates', verbose_name=_("Professional"))
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True, null=True)
    services = models.ManyToManyField(Service, related_name='templates', verbose_name=_("Services"), blank=True)
    
    base_price = models.DecimalField(
        _("Base Price"),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'), 
        help_text=_("The starting price for the template package."),
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        _("Currency"),
        max_length=3,
        choices=[('EUR', 'Euro'), ('USD', 'US Dollar'), ('GBP', 'British Pound')],
        default='EUR',
        help_text=_("The currency for the template's pricing.")
    )
    default_guests = models.PositiveIntegerField(
        _("Number of Guests"),
        default=0,
        help_text=_("The number of guests included in the base price. Users can adjust this.")
    )
    price_per_additional_guest = models.DecimalField(
        _("Additional Guest Price"),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Price for each guest above the default number."),
        validators=[MinValueValidator(0)]
    )
    
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class TemplateItemGroup(models.Model):  # New model for item groups
    """
    Represents a group of items within a template.
    Professional defines how many items from this group are mandatory.
    """
    template = models.ForeignKey(
        Template, 
        on_delete=models.CASCADE, 
        related_name='item_groups',
        verbose_name=_("Template")
    )
    name = models.CharField(
        _("Group Name"), 
        max_length=200,
        help_text=_("e.g., 'Main Course', 'Desserts', 'Decorations'")
    )
    position = models.PositiveIntegerField(
        _("Position"),
        default=0,
        help_text=_("Display order of this group")
    )
    mandatory_count = models.PositiveIntegerField(
        _("Mandatory Items Count"),
        default=0,
        help_text=_("Number of items customer must select from this group (0 = optional)")
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Template Item Group")
        verbose_name_plural = _("Template Item Groups")
        ordering = ['template', 'position', 'name']

    def __str__(self):
        return f"{self.template.title} - {self.name}"

    def clean(self):
        # Only validate if the group has been saved and has items
        if self.pk and self.mandatory_count > self.items.count():  # Only check items if pk exists
            raise ValidationError({
                'mandatory_count': _(
                    "Mandatory count (%(count)d) cannot exceed the number of items in the group (%(total)d)."
                ) % {'count': self.mandatory_count, 'total': self.items.count()}
            })


class TemplateItemGroupItem(models.Model):  # New model for items in groups
    """
    Links specific items to a template item group.
    """
    group = models.ForeignKey(
        TemplateItemGroup,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Group")
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='template_group_items',
        verbose_name=_("Item")
    )
    position = models.PositiveIntegerField(
        _("Position"),
        default=0,
        help_text=_("Display order within the group")
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)  # Added missing updated_at field
    
    class Meta:
        verbose_name = _("Template Group Item")
        verbose_name_plural = _("Template Group Items")
        ordering = ['group', 'position', 'item__title']
        unique_together = ['group', 'item']  # prevent duplicate items in same group

    def __str__(self):
        return f"{self.group.name} - {self.item.title}"


class TemplateImage(models.Model):
    template = models.ForeignKey(Template, related_name='images', on_delete=models.CASCADE, verbose_name=_("Template"))
    image = models.ImageField(_("Image"), upload_to='template_images/')
    is_default = models.BooleanField(_("Default Image"), default=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Template Image")
        verbose_name_plural = _("Template Images")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['template'], condition=models.Q(is_default=True), name='unique_default_image_per_template')
        ]

    def __str__(self):
        return f"Image for {self.template.title}{' (Default)' if self.is_default else ''}"

    def save(self, *args, **kwargs):
        if self.is_default:
            TemplateImage.objects.filter(template=self.template).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)