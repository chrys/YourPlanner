from django.contrib import admin
from .models import Professional, Customer, ProfessionalCustomerLink

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'specialization', 'rating']
    search_fields = ['user__username', 'user__email', 'title', 'specialization']
    list_filter = ['rating']
    filter_horizontal = ['labels']  # Add the labels field

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'preferred_currency', 'role']
    search_fields = ['user__username', 'user__email', 'company_name']
    list_filter = ['preferred_currency', 'role']
    filter_horizontal = ['labels']  # Add the labels field

@admin.register(ProfessionalCustomerLink)
class ProfessionalCustomerLinkAdmin(admin.ModelAdmin):
    list_display = ['professional', 'customer', 'status', 'relationship_start_date']
    list_filter = ['status', 'relationship_start_date']
    search_fields = ['professional__user__username', 'customer__user__username', 'notes']
