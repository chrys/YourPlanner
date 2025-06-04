from django.contrib import admin
from .models import Service, Item, Price, ServiceCategory

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

class PriceInline(admin.TabularInline):
    model = Price
    extra = 0

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    readonly_fields = ['show_prices']

    def show_prices(self, obj):
        return ", ".join(
            f"{price.amount} {price.currency} ({price.get_frequency_display()})"
            for price in obj.prices.all()
        )
    show_prices.short_description = "Prices"

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'professional', 'created_at']
    list_filter = ['professional', 'is_active', 'featured']
    search_fields = ['title', 'professional__user__email', 'professional__title']
    inlines = [ItemInline]
    filter_horizontal = ('labels',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('professional', 'category', 'title', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
        ('Labels', {
            'fields': ('labels',)
        }),
        ('Advanced', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'service', 'sku', 'stock', 'is_active']
    list_filter = ['service', 'is_active']
    search_fields = ['title', 'description', 'sku', 'service__title']
    inlines = [PriceInline]
    filter_horizontal = ('labels',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('service', 'title', 'description', 'image')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock', 'is_active')
        }),
        ('Display', {
            'fields': ('position',)
        }),
        ('Labels', {
            'fields': ('labels',)
        }),
        ('Advanced', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['item', 'amount', 'currency', 'frequency', 'is_active']
    list_filter = ['currency', 'frequency', 'is_active']
    search_fields = ['item__title', 'description']
    readonly_fields = ['created_at', 'updated_at']

