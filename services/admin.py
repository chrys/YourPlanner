from django.contrib import admin
from .models import Service, Item, Price, ServiceCategory

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

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'professional', 'created_at']
    list_filter = ['professional']
    search_fields = ['title', 'professional__user__email', 'professional__title']
    # CHANGED: Added PriceInline to show service-level prices
    inlines = [ItemInline, PriceInline]
    filter_horizontal = ['labels']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'service', 'is_active']
    list_filter = ['service', 'is_active']
    search_fields = ['title', 'description']
    filter_horizontal = ['labels']  # Add the labels field

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    # CHANGED: Updated to show both service and item relationships
    list_display = ['get_price_target', 'amount', 'currency', 'frequency', 'is_active']
    list_filter = ['currency', 'frequency', 'is_active', 'service', 'item']
    search_fields = ['item__title', 'service__title', 'description']
    filter_horizontal = ['labels']
    
    # CHANGED: Added method to display whether price is for service or item
    def get_price_target(self, obj):
        if obj.service:
            return f"Service: {obj.service.title}"
        elif obj.item:
            return f"Item: {obj.item.title}"
        return "Unlinked"
    get_price_target.short_description = "Target"

