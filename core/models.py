from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


class TimeStampedModel(models.Model):
    """
    An abstract base model that provides self-updating
    created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    """
    A manager that returns only active objects.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class StandardPage(Page): 
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
