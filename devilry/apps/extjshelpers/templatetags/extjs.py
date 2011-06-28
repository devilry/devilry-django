from django.db.models import fields
from django import template
from django.utils.safestring import mark_safe
from django.utils import simplejson as json

register = template.Library()



def _recurse_get_fkfield(modelcls, path):
    cur = modelcls._meta.get_field(path.pop(0))
    if not path:
        return cur
    else:
        return _recurse_get_fkfield(cur.related.model, path)

def _iter_fields(simplifiedcls):
    meta = simplifiedcls._meta
    for fieldname in meta.resultfields:
        if "__" in fieldname:
            path = fieldname.split('__')
            yield fieldname, _recurse_get_fkfield(meta.model, path)
        else:
            yield fieldname, meta.model._meta.get_field(fieldname)


def _get_extjs_modelname(restfulcls):
    simplified = restfulcls._meta.simplified
    return '{module}.{name}'.format(module=simplified.__module__, name=simplified.__name__)


def _field_to_extjs_type(field, fieldname):
    """ Convert django field to extjs  field type. """
    if isinstance(field, fields.IntegerField):
        return 'int'
    elif isinstance(field, fields.AutoField):
        return 'int'
    else:
        return 'string'


@register.filter
def extjs_model(restfulcls):
    modelfields = []
    for fieldname, field in _iter_fields(restfulcls._meta.simplified):
        exttype = _field_to_extjs_type(field, fieldname)
        modelfields.append(dict(name=fieldname, type=exttype))
    for fieldname in restfulcls._meta.urlmap:
        modelfields.append(dict(name=fieldname, type='string'))
    idprop = 'id'
    modelname = _get_extjs_modelname(restfulcls)
    modelfields = json.dumps(modelfields)
    resturl = restfulcls.get_rest_url()
    js = """
    Ext.define('%(modelname)s', {
        extend: 'Ext.data.Model',
        fields: %(modelfields)s,
        idProperty: '%(idprop)s',
        proxy: {
            type: 'rest',
            url: '%(resturl)s',
            extraParams: {data_in_qrystring: true},
            reader: {
                type: 'json',
                root: 'items'
            },
            writer: {
                type: 'json'
            }
        }
    });""" % vars()
    return mark_safe(js)


@register.filter
def extjs_store(restfulcls):
    modelname = _get_extjs_modelname(restfulcls)
    js = """ Ext.create('Ext.data.Store', {
        model: '%(modelname)s',
        autoLoad: true,
        autoSync: true
    });""" % vars()
    return mark_safe(js)
