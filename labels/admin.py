from django.contrib import admin
from .models import Label

#@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'description')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

