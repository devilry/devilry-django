from django import template
from django.utils.safestring import mark_safe
from ..modelintegration import (restfulcls_to_extjsmodel, get_extjs_modelname,
                                restfulcls_to_extjscomboboxmodel)
from ..storeintegration import restfulcls_to_extjsstore
from ..formintegration import restfulcls_to_extjsformitems

register = template.Library()


@register.filter
def extjs_model(restfulcls, result_fieldgroups=None):
    if result_fieldgroups:
        result_fieldgroups = result_fieldgroups.split(',')
    else:
        result_fieldgroups = []
    js = restfulcls_to_extjsmodel(restfulcls, result_fieldgroups)
    return mark_safe(js)

@register.filter
def extjs_combobox_model(restfulcls):
    js = restfulcls_to_extjscomboboxmodel(restfulcls)
    return mark_safe(js)

@register.filter
def extjs_store(restfulcls):
    js = restfulcls_to_extjsstore(restfulcls)
    return mark_safe(js)

@register.filter
def extjs_form_items(restfulcls):
    js = restfulcls_to_extjsformitems(restfulcls)
    return mark_safe(js)

@register.filter
def get_extjsname_from_class(restfulcls):
    js = get_extjs_modelname(restfulcls)
    return mark_safe("'{0}'".format(js))
