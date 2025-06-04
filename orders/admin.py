# filepath: /Users/chrys/Projects/YourPlanner/orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'status', 'total_amount', 'created_at']
    list_filter = ['status']
    filter_horizontal = ['labels']  # Add the labels field

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'item', 'quantity', 'price_amount_at_order']
    list_filter = ['order']
    filter_horizontal = ['labels']  # Add the labels field

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['new_status']
    search_fields = ['order__id', 'notes']

