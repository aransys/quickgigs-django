from django import template

register = template.Library()

@register.filter
def currency(value):
    """Format a decimal value as currency with commas"""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return value

@register.filter  
def currency_simple(value):
    """Simple currency format without decimals if whole number"""
    try:
        if float(value) == int(float(value)):
            return f"${int(float(value)):,}"
        else:
            return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return value 