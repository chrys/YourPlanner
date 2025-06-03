from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key), 0)  # Convert key to string and default to 0

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