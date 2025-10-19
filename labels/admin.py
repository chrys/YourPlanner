from django.contrib import admin
from .models import Label

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'label_type', 'visible_to_client')  # Change: Display these columns in the admin list view
    list_filter = ('label_type', 'visible_to_client', 'created_at')  # Change: Add filters for easier navigation
    search_fields = ('name', 'description')  # Change: Enable search by name and description
    ordering = ('name',)  # Change: Order labels by name by default

