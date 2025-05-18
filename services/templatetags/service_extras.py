from django import template
register = template.Library()

@register.filter
def first_active(prices):
    return prices.filter(is_active=True).first()