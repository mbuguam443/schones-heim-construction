from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter
def client_name(user):
    try:
        return user.client_profile.full_name
    except ObjectDoesNotExist:
        return ''
