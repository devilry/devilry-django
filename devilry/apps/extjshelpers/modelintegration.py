import json
from django.db.models import fields


def _djangofield_to_extjstype(field):
    """ Convert django field to extjs  field type. """
    if isinstance(field, fields.IntegerField):
        return dict(type='int')
    elif isinstance(field, fields.AutoField):
        return dict(type='int')
    elif isinstance(field, fields.DateTimeField):
        return dict(type='date')
    elif isinstance(field, fields.BooleanField):
        return dict(type='bool')
    else:
        return dict(type='auto')



def _recurse_get_fkfield(modelcls, path):
    cur = modelcls._meta.get_field(path.pop(0))
    if not path:
        return cur
    else:
        return _recurse_get_fkfield(cur.related.parent_model, path)


def _iter_fields(simplifiedcls, result_fieldgroups):
    meta = simplifiedcls._meta
    for fieldname in meta.resultfields.aslist(result_fieldgroups):
        if "__" in fieldname:
            path = fieldname.split('__')
            yield fieldname, _recurse_get_fkfield(meta.model, path)
        else:
            yield fieldname, meta.model._meta.get_field(fieldname)



def get_extjs_modelname(restfulcls):
    simplified = restfulcls._meta.simplified
    return '{module}.{name}'.format(module=simplified.__module__, name=simplified.__name__)


def restfulcls_to_extjsmodel(restfulcls, result_fieldgroups=[]):
    modelfields = []
    for fieldname, field in _iter_fields(restfulcls._meta.simplified,
                                         result_fieldgroups):
        exttype = _djangofield_to_extjstype(field)
        exttype['name'] = fieldname
        modelfields.append(exttype)
    #for fieldname in restfulcls._meta.urlmap:
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
                    result_fieldgroups: {result_fieldgroups}
                }},
                reader: {{
                    type: 'json',
                    root: 'items'
                }},
                writer: {{
                    type: 'json'
                }}
            }}
        }})""".format(modelname = get_extjs_modelname(restfulcls),
                      modelfields = json.dumps(modelfields),
                      idprop = 'id', # TODO: metaoption
                      resturl = restfulcls.get_rest_url(),
                      result_fieldgroups=json.dumps(result_fieldgroups))


def restfulcls_to_extjscomboboxmodel(restfulcls):
    """ Create a extjs model using the ``restfulcls.ExtjsModelMeta.combobox_fieldgroups`` """
    return restfulcls_to_extjsmodel(restfulcls, restfulcls._extjsmodelmeta.combobox_fieldgroups)
