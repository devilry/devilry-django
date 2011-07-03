from modelintegration import get_extjs_modelname
from fieldintegration import field_to_extjstype
import json

def _iter_search_fields(simplifiedcls):
    meta = simplifiedcls._meta
    for fieldname in meta.searchfields.aslist():
        yield fieldname

def get_extjs_modelfields(restfulmodelcls):

    modelfields = []

    for fieldname in _iter_search_fields(restfulmodelcls._meta.simplified):
        modelfields.append(dict(name=fieldname,))
        
    modelitems = ""

    for item in modelfields:
        modelitems += "{{fieldLabel: '{fl}',".format(fl=item['name'])
        modelitems += "name: '{name}'".format(name=item['name'])
        modelitems += "},\n"

    return modelitems

def restfulmodelcls_to_extjsforms(restfulmodelcls):    
    return """Ext.create('Ext.form.Panel, {{
                  renderTo: 'form-example',
                  title: 'test',
                  model: '{modelname}',
                  items: [{modelitems}]
                  }}""".format(modelname=get_extjs_modelname(restfulmodelcls),
                              modelitems=get_extjs_modelfields(restfulmodelcls))
