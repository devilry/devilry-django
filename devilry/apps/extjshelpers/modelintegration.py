import json
from django.db.models import fields


def field_to_extjstype(field, fieldname):
    """ Convert django field to extjs  field type. """
    if isinstance(field, fields.IntegerField):
        return dict(type='int')
    elif isinstance(field, fields.AutoField):
        return dict(type='int')
    elif isinstance(field, fields.DateTimeField):
        return dict(type='date')
    else:
        return dict(type='auto')



def _recurse_get_fkfield(modelcls, path):
    cur = modelcls._meta.get_field(path.pop(0))
    if not path:
        return cur
    else:
        return _recurse_get_fkfield(cur.related.model, path)


def _iter_fields(simplifiedcls, result_fieldgroups):
    meta = simplifiedcls._meta
    for fieldname in meta.resultfields.aslist(result_fieldgroups):
        if "__" in fieldname:
            path = fieldname.split('__')
            yield path[0], _recurse_get_fkfield(meta.model, path)
        else:
            yield fieldname, meta.model._meta.get_field(fieldname)



def get_extjs_modelname(restfulmodelcls):
    simplified = restfulmodelcls._meta.simplified
    return '{module}.{name}'.format(module=simplified.__module__, name=simplified.__name__)


def restfulmodelcls_to_extjsmodel(restfulmodelcls, result_fieldgroups=[]):
    modelfields = []
    for fieldname, field in _iter_fields(restfulmodelcls._meta.simplified,
                                         result_fieldgroups):
        exttype = field_to_extjstype(field, fieldname)
        exttype['name'] = fieldname
        modelfields.append(exttype)
    #for fieldname in restfulmodelcls._meta.urlmap:
        #modelfields.append(dict(name=fieldname, type='string'))

    return """Ext.define('{modelname}', {{
            extend: 'Ext.data.Model',
            fields: {modelfields},
            idProperty: '{idprop}',
            proxy: {{
                type: 'rest',
                url: '{resturl}',
                extraParams: {{
                    getdata_in_qrystring: true,
                    result_fieldgroups: '{result_fieldgroups}'
                }},
                reader: {{
                    type: 'json',
                    root: 'items'
                }},
                writer: {{
                    type: 'json'
                }}
            }}
        }})""".format(modelname = get_extjs_modelname(restfulmodelcls),
                      modelfields = json.dumps(modelfields),
                      idprop = 'id', # TODO: metaoption
                      resturl = restfulmodelcls.get_rest_url(),
                      result_fieldgroups=','.join(result_fieldgroups))
