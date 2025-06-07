from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from users.models import Professional # Adjusted: Removed UserProfile, assuming Professional links directly or via User
from services.models import Service

class Template(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='templates', verbose_name=_("Professional"))
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True, null=True)
    services = models.ManyToManyField(Service, related_name='templates', verbose_name=_("Services"), blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class TemplateImage(models.Model):
    template = models.ForeignKey(Template, related_name='images', on_delete=models.CASCADE, verbose_name=_("Template"))
    image = models.ImageField(_("Image"), upload_to='template_images/') # Ensure this is NOT blank=True, null=True
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
