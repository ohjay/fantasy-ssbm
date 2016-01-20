from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def no_spaces(value):
    """Removes all spaces from a string."""
    return value.replace(' ', '')
