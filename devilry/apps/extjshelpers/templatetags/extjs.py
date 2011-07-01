from django import template
from django.utils.safestring import mark_safe
from ..modelintegration import restfulmodelcls_to_extjsmodel
from ..storeintegration import restfulmodelcls_to_extjsstore

register = template.Library()


@register.filter
def extjs_model(restfulmodelcls):
    js = restfulmodelcls_to_extjsmodel(restfulmodelcls)
    return mark_safe(js)


@register.filter
def extjs_store(restfulmodelcls):
    js = restfulmodelcls_to_extjsstore(restfulmodelcls)
    return mark_safe(js)
