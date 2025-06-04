from django.contrib import admin
from .models import Professional, Customer, ProfessionalCustomerLink

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'specialization', 'rating', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'specialization')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('labels',)
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'title', 'specialization', 'bio', 'profile_image')
        }),
        ('Contact Information', {
            'fields': ('contact_hours',)
        }),
        ('Rating', {
            'fields': ('rating',)
        }),
        ('Labels', {
            'fields': ('labels',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'preferred_currency', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name')
    list_filter = ('preferred_currency', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('labels',)
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'company_name')
        }),
        ('Address Information', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Preferences', {
            'fields': ('preferred_currency', 'marketing_preferences')
        }),
        ('Labels', {
            'fields': ('labels',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProfessionalCustomerLink)
class ProfessionalCustomerLinkAdmin(admin.ModelAdmin):
    list_display = ('professional', 'customer', 'status', 'relationship_start_date', 'last_interaction_date')
    list_filter = ('status', 'relationship_start_date', 'preferred_communication')
    search_fields = ('professional__user__username', 'customer__user__username', 'notes')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Relationship', {
            'fields': ('professional', 'customer', 'status', 'relationship_start_date')
        }),
        ('Communication', {
            'fields': ('preferred_communication', 'last_interaction_date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

