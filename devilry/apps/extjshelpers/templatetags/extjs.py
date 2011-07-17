from django import template
from django.utils.safestring import mark_safe
from ..modelintegration import (restfulcls_to_extjsmodel, get_extjs_modelname,
                                restfulcls_to_extjscomboboxmodel)
from ..storeintegration import restfulcls_to_extjsstore
from ..formintegration import (restfulcls_to_extjsformitems,
                               restfulcls_to_foreignkeylist)

register = template.Library()


@register.filter
def extjs_model(restfulcls, result_fieldgroups=None):
    """
    Create an extjs model from the given restful class.
    Uses :func:`~devilry.apps.extjshelpers.modelintegration.restfulcls_to_extjsmodel`.

    Example (javascript+django templatate):

    .. code-block:: javascript

        var deliverymodel = {{ RestfulSimplifiedDelivery|extjs_model }};

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
    js = restfulcls_to_extjscomboboxmodel(restfulcls)
    return mark_safe(js)

@register.filter
def extjs_store(restfulcls, pagesize=None):
    """
    Create an extjs store from the given restful class.
    Uses :func:`~devilry.apps.extjshelpers.storeintegration.restfulcls_to_extjsstore`.

    Example (javascript+django templatate):

    .. code-block:: javascript

        var deliverystore = {{ RestfulSimplifiedDelivery|extjs_store }};

    :param restfulcls: Forwarded directly to
        :func:`~devilry.apps.extjshelpers.storeintegration.restfulcls_to_extjsstore`.
    :param result_fieldgroups:
        :func:`~devilry.apps.extjshelpers.storeintegration.restfulcls_to_extjsstore`.
    """
    js = restfulcls_to_extjsstore(restfulcls, pagesize=pagesize)
    return mark_safe(js)

@register.filter
def extjs_form_items(restfulcls):
    js = restfulcls_to_extjsformitems(restfulcls)
    return mark_safe(js)

@register.filter
def extjs_foreignkeys(restfulcls):
    js = restfulcls_to_foreignkeylist(restfulcls)
    return mark_safe(js)

@register.filter
def get_extjsname_from_class(restfulcls):
    js = get_extjs_modelname(restfulcls)
    return mark_safe("'{0}'".format(js))
