from django.contrib import admin
from .models import Service, Item, Price

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
    list_filter = ['professional']
    search_fields = ['title', 'professional__user__email', 'professional__title']
    inlines = [ItemInline]