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
    Ext.define('StatConfig', {
        extend: 'Ext.data.Model',
        fields: %(fields)s,
        idProperty: '%(idprop)s'
    });"""

    modelfields = []
    for fieldname, field in _iter_fields(simplified):
        exttype = cls.field_to_extjs_type(field, fieldname)
        modelfields.append(dict(name='fieldname', type=exttype))
    idprop = 'id'
    cls.extjs_model = tpl % dict(idprop=idprop, fields=json.dumps(modelfields))


def extjs_modelapi(cls):
    _create_extjs_model_field(cls)
    return cls


class ExtJsMixin(object):
    @classmethod
    def field_to_extjs_type(cls, field, fieldname):
        if isinstance(field, fields.IntegerField):
            return 'int'
        else:
            return 'string'
