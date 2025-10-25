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
    
@admin.register(Agent)  # CHANGE: Register Agent admin
class AgentAdmin(admin.ModelAdmin):  # CHANGE: Simplified AgentAdmin (no permissions management)
    """Admin interface for managing Agents. Only admins can create/edit agents."""
    
    list_display = [  # CHANGE: Display these columns in list view
        'user', 'title', 'department', 'status', 'get_assigned_orders_count'
    ]
    
    list_filter = [  # CHANGE: Add filters
        'status', 'department', 'created_at'
    ]
    
    search_fields = [  # CHANGE: Enable search
        'title', 'user__email', 'user__username', 'department', 'bio'
    ]
    
    readonly_fields = [  # CHANGE: Read-only fields
        'created_at', 'updated_at', 'get_assigned_orders_count'
    ]
    
    fieldsets = (  # CHANGE: Organize fields in sections
        ('User Information', {
            'fields': ('user',)
        }),
        ('Agent Profile', {
            'fields': ('title', 'bio', 'department', 'profile_image', 'contact_phone')
        }),
        ('Status', {
            'fields': ('status',),
            'description': 'Set agent status (Active/Inactive/Suspended)'  # CHANGE: Simplified description
        }),
        ('Additional Information', {
            'fields': ('notes', 'labels'),
            'classes': ('collapse',)  # CHANGE: Collapsible section
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['labels']  # CHANGE: Better UI for M2M field
    
    def get_readonly_fields(self, request, obj=None):  # CHANGE: Additional read-only logic
        """Prevent non-superusers from modifying certain fields."""
        readonly = list(self.readonly_fields)
        
        # CHANGE: Non-superusers cannot change user or status
        if not request.user.is_superuser:
            readonly.extend(['user', 'status'])
        
        return readonly
    
    def get_assigned_orders_count(self, obj):  # CHANGE: Display number of assigned orders
        """Show count of orders assigned to this agent."""
        count = obj.assigned_orders.count() if obj else 0  # CHANGE: Use assigned_orders relation
        return f"{count} orders"
    
    get_assigned_orders_count.short_description = "Assigned Orders"  # CHANGE: Column header
    
    def save_model(self, request, obj, form, change):  # CHANGE: Log admin actions
        """Override save to log admin actions."""
        if change:  # CHANGE: If updating
            # You could add logging here if needed
            pass
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):  # CHANGE: Only superusers can create agents
        """Only superusers can create new agents."""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):  # CHANGE: Only superusers can delete agents
        """Only superusers can delete agents."""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):  # CHANGE: Only staff can edit agents
        """Only superusers or staff can edit agents."""
        return request.user.is_staff