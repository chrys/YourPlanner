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

<<<<<<< HEAD
#admin.site.register(Label, ConfigurationAdmin)
=======
# admin.site.register(Label, ConfigurationAdmin) # Removed to prevent AlreadyRegistered error
>>>>>>> 9ffff20290f189ac636399c97d41263a3e8fc74e
