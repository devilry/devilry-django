from django import template
from django.utils.translation import get_language

from devilry.django_decoupled_docs.registry import documentationregistry


register = template.Library()

@register.simple_tag()
def decoupled_docs_url(documentid):
    current_language = get_language()
    return documentationregistry.get(documentid, current_language)
