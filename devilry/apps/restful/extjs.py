from django.db.models import fields
from django.utils import simplejson as json


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


def _create_extjs_model_field(cls):
    simplified = cls._meta.simplified
    tpl = """
    Ext.define('%(modelname)s', {
        extend: 'Ext.data.Model',
        fields: %(modelfields)s,
        idProperty: '%(idprop)s'
    });"""

    modelfields = []
    for fieldname, field in _iter_fields(simplified):
        exttype = cls.field_to_extjs_type(field, fieldname)
        modelfields.append(dict(name=fieldname, type=exttype))
    idprop = 'id'
    modelname = simplified._meta.model._meta.db_table
    modelfields = json.dumps(modelfields)
    cls._meta.extjs_modelname = modelname
    cls.extjs_model_class = tpl % vars()


def extjs_modelapi(cls):
    _create_extjs_model_field(cls)
    return cls


class ExtJsMixin(object):
    @classmethod
    def field_to_extjs_type(cls, field, fieldname):
        #print type(field)
        if isinstance(field, fields.IntegerField):
            return 'int'
        elif isinstance(field, fields.AutoField):
            return 'int'
        else:
            return 'string'

    @classmethod
    def get_extjs_store_object(cls):
        modelname = cls._meta.extjs_modelname
        resturl = cls.get_rest_url()
        return """ Ext.create('Ext.data.Store', {
            model: '%(modelname)s',
            autoLoad: true,
            autoSync: true,
            proxy: {
                type: 'rest',
                url: '%(resturl)s',
                reader: {
                    type: 'json',
                    root: 'items'
                },
                writer: 'json'
            }
        });""" % vars()
