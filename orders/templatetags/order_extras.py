from django import template
register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Allows accessing dictionary items with a variable key in Django templates."""
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.filter
def first_active(prices):
    return prices.filter(is_active=True).first()

@register.simple_tag
def order_status_badge(status):
    if status == "PENDING":
        return "bg-warning"
    elif status == "CONFIRMED":
        return "bg-info"
    elif status == "COMPLETED":
        return "bg-success"
    elif status == "CANCELLED":
        return "bg-danger"
    return "bg-secondary"