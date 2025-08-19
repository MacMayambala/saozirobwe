from django import template

register = template.Library()

@register.filter
def abs_filter(value):
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value