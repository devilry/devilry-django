from django import template
from django.utils.safestring import mark_safe
from ..modelintegration import (restfulcls_to_extjsmodel, get_extjs_modelname,
                                restfulcls_to_extjscomboboxmodel)
from ..storeintegration import (restfulcls_to_extjsstore, get_extjs_storeid)
from ..formintegration import (restfulcls_to_extjsformitems,
                               restfulcls_to_foreignkeylist)

register = template.Library()


@register.filter
def extjs_model(restfulcls, result_fieldgroups=None):
    """
    Create an extjs model from the given restful class.
    Uses :func:`~devilry.apps.extjshelpers.modelintegration.restfulcls_to_extjsmodel`.

    :param restfulcls: Forwarded directly to :func:`~devilry.apps.extjshelpers.modelintegration.restfulcls_to_extjsmodel`.
    :param result_fieldgroups:
        A string separated by ``","``. The string is split and forwarded to
        :func:`~devilry.apps.extjshelpers.modelintegration.restfulcls_to_extjsmodel`.
    """
    if result_fieldgroups:
        result_fieldgroups = result_fieldgroups.split(',')
    else:
        result_fieldgroups = []
    js = restfulcls_to_extjsmodel(restfulcls, result_fieldgroups)
    return mark_safe(js)

@register.filter
def extjs_combobox_model(restfulcls):
    """
    Wrapper for :func:`~devilry.apps.extjshelpers.modelintegration.restfulcls_to_extjscomboboxmodel`.
    """
    js = restfulcls_to_extjscomboboxmodel(restfulcls)
    return mark_safe(js)

@register.filter
def extjs_store(restfulcls, pagesize=None):
    """
    Create an extjs store from the given restful class.
    Uses :func:`~devilry.apps.extjshelpers.storeintegration.restfulcls_to_extjsstore`.

    :param restfulcls: Forwarded directly to
        :func:`~devilry.apps.extjshelpers.storeintegration.restfulcls_to_extjsstore`.
    :param result_fieldgroups:
        :func:`~devilry.apps.extjshelpers.storeintegration.restfulcls_to_extjsstore`.
    """
    js = restfulcls_to_extjsstore(restfulcls, pagesize=pagesize)
    return mark_safe(js)

@register.filter
def extjs_form_items(restfulcls):
    """
    Wrapper for
    :func:`~devilry.apps.extjshelpers.formintegration.restfulcls_to_extjsformitems`.
    """
    js = restfulcls_to_extjsformitems(restfulcls)
    return mark_safe(js)

@register.filter
def extjs_foreignkeys(restfulcls):
    """
    Wrapper for
    :func:`~devilry.apps.extjshelpers.formintegration.restfulcls_to_foreignkeylist`.
    """
    js = restfulcls_to_foreignkeylist(restfulcls)
    return mark_safe(js)

@register.filter
def extjs_modelname(restfulcls):
    """
    Get the name of the extjs model generated by
    :func:`~devilry.extjshelpers.templatetags.extjs.extjs_model` using the same
    ``restfulcls``.

    Uses :func:`~devilry.apps.extjshelpers.modelintegration.get_extjs_modelname`.
    """
    js = get_extjs_modelname(restfulcls)
    return mark_safe("'{0}'".format(js))

@register.filter
def extjs_storeid(restfulcls):
    """
    Get the id of the extjs store generated by
    :func:`~devilry.extjshelpers.templatetags.extjs.extjs_store` using the same
    ``restfulcls``.

    Uses :func:`~devilry.apps.extjshelpers.storeintegration.get_extjs_storeid`.
    """
    js = get_extjs_storeid(restfulcls)
    return mark_safe("'{0}'".format(js))
