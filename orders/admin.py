# filepath: /Users/chrys/Projects/YourPlanner/orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'status', 'total_amount', 'created_at']
    list_filter = ['status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'item', 'quantity', 'price_amount_at_order']
    list_filter = ['order']
    
