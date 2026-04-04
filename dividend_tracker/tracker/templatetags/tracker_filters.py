from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def currency(value):
    """Format as $1,234.56"""
    if value is None:
        return '—'
    try:
        return f'${float(value):,.2f}'
    except (ValueError, TypeError):
        return '—'


@register.filter
def currency6(value):
    """Format as $0.123456 (6 decimal places for per-share amounts)"""
    if value is None:
        return '—'
    try:
        return f'${float(value):.6f}'
    except (ValueError, TypeError):
        return '—'


@register.filter
def percentage(value, decimals=2):
    """Format as 4.50%"""
    if value is None:
        return '—'
    try:
        return f'{float(value):.{decimals}f}%'
    except (ValueError, TypeError):
        return '—'


@register.filter
def abs_value(value):
    """Absolute value."""
    if value is None:
        return None
    try:
        return abs(value)
    except (ValueError, TypeError):
        return value


@register.filter
def gain_loss_class(value):
    """Return CSS class based on positive/negative value."""
    if value is None:
        return ''
    try:
        return 'positive' if float(value) >= 0 else 'negative'
    except (ValueError, TypeError):
        return ''
