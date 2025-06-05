from django.contrib import admin
from labels.models import Label

class ConfigurationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Labels as part of system configuration.
    """
    list_display = ('name', 'description', 'color', 'type')
    list_filter = ('type',)
    search_fields = ('name', 'description')
    ordering = ('name',)

#admin.site.register(Label, ConfigurationAdmin)
