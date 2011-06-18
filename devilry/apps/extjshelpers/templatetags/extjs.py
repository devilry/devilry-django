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
    return simplified._meta.model._meta.db_table


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
    js = """
    Ext.define('%(modelname)s', {
        extend: 'Ext.data.Model',
        fields: %(modelfields)s,
        idProperty: '%(idprop)s'
    });""" % vars()
    return mark_safe(js)


@register.filter
def extjs_store(restfulcls):
    modelname = _get_extjs_modelname(restfulcls)
    resturl = restfulcls.get_rest_url()
    js = """ Ext.create('Ext.data.Store', {
        model: '%(modelname)s',
        autoLoad: true,
        autoSync: true,
        proxy: {
            type: 'rest',
            url: '%(resturl)s',
            extraParams: {use_getqry: true},
            reader: {
                type: 'json',
                root: 'items'
            },
            writer: {
                type: 'json',
                allowSingle: false
            }
        }
    });""" % vars()
    return mark_safe(js)
