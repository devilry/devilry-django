import json
from django.db.models import fields

from devilry.simplified import OneToMany



def _djangofield_to_extjstype(field):
    """ Convert django field to extjs  field type. """
    if isinstance(field, fields.IntegerField):
        return dict(type='int')
    elif isinstance(field, fields.AutoField):
        return dict(type='int')
    elif isinstance(field, fields.DateTimeField):
        return dict(type='date', dateFormat='Y-m-d\\TH:i:s')
    elif isinstance(field, fields.BooleanField):
        return dict(type='bool')
    else:
        return dict(type='auto')



def _recurse_get_fkfield(modelcls, path):
    fieldname = path.pop(0)
    try:
        cur = modelcls._meta.get_field(fieldname)
    except fields.FieldDoesNotExist, e:
        # We assume this is a ManyToMany field if it is not a normal field
        return dict(type='auto')
    if not path:
        return _djangofield_to_extjstype(cur)
    else:
        return _recurse_get_fkfield(cur.related.parent_model, path)


def _iter_fields(simplifiedcls, result_fieldgroups):
    meta = simplifiedcls._meta
    for fieldname in meta.resultfields.aslist(result_fieldgroups):
        if isinstance(fieldname, OneToMany):
            yield fieldname.related_field, dict(type='auto')
        elif "__" in fieldname:
            path = fieldname.split('__')
            yield fieldname, _recurse_get_fkfield(meta.model, path)
        else:
            if fieldname in simplifiedcls._meta.annotated_fields:
                extjstype = dict(type='auto')
            else:
                extjstype =_djangofield_to_extjstype(meta.model._meta.get_field(fieldname)) 
            yield fieldname, extjstype



def get_extjs_modelname(restfulcls, modelnamesuffix=''):
    """
    Get the ExtJS model name for the given restful class.
    Generated from the module name and class name of
    ``restfulcls._meta.simplified``

    :param modelnamesuffix:
        Suffixed to the generated model name.
    """
    simplified = restfulcls._meta.simplified
    clsname = simplified.__name__
    modulepath = simplified.__module__.replace('.' + clsname.lower(), '')
    modelname = '{module}.{name}{modelnamesuffix}'.format(module=modulepath,
                                                          name=clsname,
                                                          modelnamesuffix=modelnamesuffix)
    return modelname

def restfulcls_to_extjsmodel(restfulcls, result_fieldgroups=[], modelnamesuffix='', pretty=False):
    """
    Create an extjs model from the given restful class.

    :param restfulcls: A class defined using the :ref:`RESTful API <restful>`.
    :param result_fieldgroups:
        ``result_fieldgroups`` is added as additional parameters to the proxy,
        which means that the parameter is forwarded to
        :meth:`devilry.simplified.SimplifiedModelApi.search` on the server after
        passing through validations in the RESTful wrapper.
    :param modelnamesuffix:
        See :func:`~devilry.apps.extjshelpers.modelintegration.get_extjs_modelname`.
    :param pretty:
        Prettyformat output.
    """
    modelfields = []
    for fieldname, exttype in _iter_fields(restfulcls._meta.simplified,
                                           result_fieldgroups):
        exttype['name'] = fieldname
        modelfields.append(exttype)
    for fake_fieldname in restfulcls._meta.simplified._meta.fake_editablefields:
        modelfields.append({'name': fake_fieldname, 'type': 'auto'})
    modelmeta = restfulcls._meta.simplified._meta.model._meta
    js_result_fieldgroups = json.dumps(result_fieldgroups) # Notice how this is json encoded and added as a string to the JS. This is because we want to send it back as a JSON encoded string to be decoded on the server. Also note that we surround this with '' below. This assumes that json uses "" for strings, which we hope is universal, at least for the json module in python?
    if pretty:
        jsmodelfields = '\n    '.join(json.dumps(modelfields, indent=4).split('\n'))
    else:
        jsmodelfields = json.dumps(modelfields)
    return """
/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({{
 *        enabled: true,
 *        paths: {{
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }}
 *    }});
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('{modelname}', {{
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: {jsmodelfields},
    idProperty: '{idprop}',
    proxy: {{
        type: 'devilryrestproxy',
        url: '{resturl}',
        headers: {{
            'X_DEVILRY_USE_EXTJS': true
        }},
        extraParams: {{
            getdata_in_qrystring: true,
            result_fieldgroups: '{js_result_fieldgroups}'
        }},
        reader: {{
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        }},
        writer: {{
            type: 'json'
        }}
    }}
}})""".format(modelname = get_extjs_modelname(restfulcls, modelnamesuffix),
              jsmodelfields = jsmodelfields,
              idprop = modelmeta.pk.name,
              resturl = restfulcls.get_rest_url(),
              js_result_fieldgroups=js_result_fieldgroups)



def _indent(string, spaces):
    indent = '\n' + ' ' * spaces
    return indent.join(string.split('\n'))

def _get_belongsto():
    pass

def export_restfulcls_to_extjsmodel(restfulcls, result_fieldgroups=[], modelnamesuffix=''):
    """
    Create an extjs model from the given restful class.

    :param restfulcls: A class defined using the :ref:`RESTful API <restful>`.
    :param result_fieldgroups:
        ``result_fieldgroups`` is added as additional parameters to the proxy,
        which means that the parameter is forwarded to
        :meth:`devilry.simplified.SimplifiedModelApi.search` on the server after
        passing through validations in the RESTful wrapper.
    :param modelnamesuffix:
        See :func:`~devilry.apps.extjshelpers.modelintegration.get_extjs_modelname`.
    """
    modelfields = []
    for fieldname, exttype in _iter_fields(restfulcls._meta.simplified,
                                           result_fieldgroups):
        exttype['name'] = fieldname
        modelfields.append(exttype)
    for fake_fieldname in restfulcls._meta.simplified._meta.fake_editablefields:
        modelfields.append({'name': fake_fieldname, 'type': 'auto'})
    modelmeta = restfulcls._meta.simplified._meta.model._meta
    js_result_fieldgroups = json.dumps(result_fieldgroups) # Notice how this is json encoded and added as a string to the JS. This is because we want to send it back as a JSON encoded string to be decoded on the server. Also note that we surround this with '' below. This assumes that json uses "" for strings, which we hope is universal, at least for the json module in python?

    extra = ''
    belongs_to = restfulcls._meta.get_belongs_to()
    if belongs_to:
        extra += 'belongsTo: "{0}",\n'.format(get_extjs_modelname(belongs_to))
    has_many = restfulcls._meta.get_has_many()
    if has_many:
        relname = has_many._meta.simplified._meta.model.__name__.lower() + '_set'
        foreignkey = restfulcls._meta.simplified._meta.model.__name__.lower()
        hasmany_prop = dict(
            model = get_extjs_modelname(has_many),
            name = relname,
            foreignKey = foreignkey
        )
        extra += 'hasMany: {0},\n'.format(json.dumps(hasmany_prop))
    

    
    return """Ext.define('{modelname}', {{
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: {modelfields},
    idProperty: '{idprop}',
    {extra}proxy: Ext.create('devilry.extjshelpers.RestProxy', {{
        url: '{resturl}',
        extraParams: {{
            getdata_in_qrystring: true,
            result_fieldgroups: '{js_result_fieldgroups}'
        }},
        reader: {{
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        }},
        writer: {{
            type: 'json'
        }}
    }})
}})""".format(modelname = get_extjs_modelname(restfulcls, modelnamesuffix),
              modelfields = _indent(json.dumps(modelfields, indent=4), spaces=4),
              idprop = modelmeta.pk.name,
              extra = _indent(extra, spaces=4),
              resturl = restfulcls.get_rest_url(),
              js_result_fieldgroups=js_result_fieldgroups)



def restfulcls_to_extjscomboboxmodel(restfulcls, modelnamesuffix=''):
    """
    Shortcut for::

        restfulcls_to_extjsmodel(restfulcls,
                                 restfulcls._extjsmodelmeta.combobox_fieldgroups,
                                 modelnamesuffix)
    """
    return restfulcls_to_extjsmodel(restfulcls,
                                    restfulcls._extjsmodelmeta.combobox_fieldgroups,
                                    modelnamesuffix)
