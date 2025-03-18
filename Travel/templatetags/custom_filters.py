from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        # Convert value to Decimal if it's not already
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        return value * Decimal(str(arg))
    except (ValueError, TypeError, InvalidOperation):
        return Decimal('0.00')
