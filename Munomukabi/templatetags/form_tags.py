# your_app/templatetags/form_tags.py
from django import template
from django.forms import BoundField

register = template.Library()

@register.filter
def add_class(value, arg):
    """Add a CSS class to a form field."""
    if isinstance(value, BoundField):
        attrs = value.field.widget.attrs
        attrs['class'] = arg
        return value.as_widget(attrs=attrs)
    return value  # Return as-is if already rendered

@register.filter
def attr(value, arg):
    """Add an arbitrary attribute to a form field."""
    if isinstance(value, BoundField):
        attrs = value.field.widget.attrs
        attrs[arg] = arg  # e.g., 'readonly': 'readonly'
        return value.as_widget(attrs=attrs)
    return value  # Return as-is if already rendered