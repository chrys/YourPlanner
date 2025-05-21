from django import template
from services.models import Item
register = template.Library()

@register.filter
def first_active(prices):
    return prices.filter(is_active=True).first()

@register.filter
def get_active_price(prices):
    return prices.filter(is_active=True).first()

@register.simple_tag
def get_all_images():
    """Return all items with images"""
    return Item.objects.exclude(image='').exclude(image=None)
