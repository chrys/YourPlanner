from django.contrib import admin
from .models import ConfigurationCategory, ConfigurationLabel

@admin.register(ConfigurationCategory)
class ConfigurationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ConfigurationLabel)
class ConfigurationLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'is_active', 'created_at', 'updated_at')
    list_filter = ('category', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)

