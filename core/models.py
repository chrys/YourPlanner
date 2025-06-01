from django.db import models

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


# Create your models here.
