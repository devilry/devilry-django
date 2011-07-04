from django import template
from django.utils.safestring import mark_safe
from ..modelintegration import (restfulmodelcls_to_extjsmodel, get_extjs_modelname)
from ..storeintegration import restfulmodelcls_to_extjsstore
from ..formintegration import restfulmodelcls_to_extjsforms

register = template.Library()


@register.filter
def extjs_model(restfulmodelcls, result_fieldgroups=None):
    if result_fieldgroups:
        result_fieldgroups = result_fieldgroups.split(',')
    else:
        result_fieldgroups = []
    js = restfulmodelcls_to_extjsmodel(restfulmodelcls, result_fieldgroups)
    return mark_safe(js)


@register.filter
def extjs_store(restfulmodelcls):
    js = restfulmodelcls_to_extjsstore(restfulmodelcls)
    return mark_safe(js)

@register.filter
def extjs_form_items(restfulmodelcls):
    js = restfulmodelcls_to_extjsformitems(restfulmodelcls)
    return mark_safe(js)

@register.filter
def get_extjsname_from_class(restfulmodelcls):
    js = get_extjs_modelname(restfulmodelcls)
    return mark_safe(js)
