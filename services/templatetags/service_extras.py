from django import template
register = template.Library()

@register.filter
def first_active(prices):
    return prices.filter(is_active=True).first()

@register.filter
def get_active_price(prices):
    return prices.filter(is_active=True).first()