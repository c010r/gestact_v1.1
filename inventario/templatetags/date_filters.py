from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def add_days(value, days):
    """
    Agrega un número específico de días a una fecha.
    Uso: {{ fecha|add_days:30 }}
    """
    if isinstance(value, datetime):
        return value + timedelta(days=int(days))
    return value