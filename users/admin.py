from django.contrib import admin
from .models import Professional, Customer, ProfessionalCustomerLink, Agent

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'specialization', 'default', 'rating']
    list_filter = ['default', 'specialization']
    search_fields = ['title', 'user__email', 'user__username', 'specialization']
    readonly_fields = ['rating']  # Rating should be calculated, not manually set

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('default',)
        return self.readonly_fields

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            fields = [f for f in fields if f != 'default']
        return fields

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('user', 'agency_name', 'created_at')
    search_fields = ('user__username', 'user__email', 'agency_name')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    filter_horizontal = ('labels',)

# Register other models if not already registered
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'role', 'wedding_day']
    list_filter = ['role']
    search_fields = ['user__email', 'user__username', 'company_name']

@admin.register(ProfessionalCustomerLink)
class ProfessionalCustomerLinkAdmin(admin.ModelAdmin):
    list_display = ['professional', 'customer', 'status', 'relationship_start_date']
    list_filter = ['status']
    search_fields = ['professional__user__username', 'customer__user__username']
