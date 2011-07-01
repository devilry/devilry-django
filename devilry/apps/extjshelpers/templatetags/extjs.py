from django import template
from django.utils.safestring import mark_safe
from ..modelintegration import restfulcls_to_extjsmodel
from ..storeintegration import restfulcls_to_extjsstore

register = template.Library()


@register.filter
def extjs_model(restfulcls):
    js = restfulcls_to_extjsmodel(restfulcls)
    return mark_safe(js)


@register.filter
def extjs_store(restfulcls):
    js = restfulcls_to_extjsstore(restfulcls)
    return mark_safe(js)
