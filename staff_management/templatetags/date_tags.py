# E:\2025\saozirobwe\staff_management\templatetags\date_tags.py
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def is_future_date(value):
    if not value:  # Handle null or invalid dates
        return False
    today = timezone.now().date()
    return value > today