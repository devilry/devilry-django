#from modelintegration import get_extjs_modelname
from fieldintegration import djangofield_to_extjsformfield
import json

def _iter_editfields(restfulmodelcls):
    for fieldname in restfulmodelcls._meta.simplified._meta.resultfields.aslist():
        extfield = djangofield_to_extjsformfield(restfulmodelcls._meta.simplified._meta.model,
                                                 fieldname,
                                                 restfulmodelcls._meta.foreignkey_fields.get(fieldname))
        yield extfield
        #yield dict(fieldLabel = fieldname.upper(),
                   #name = fieldname,
                   #xtype = 'textfield')

def _get_extjs_modelfields(restfulmodelcls):
    modelitems = [fieldspec \
            for fieldspec in _iter_editfields(restfulmodelcls)]
    return modelitems

#def restfulmodelcls_to_extjsforms(restfulmodelcls):
    #return """model: '{modelname}',
              #items: {modelitems}""".format(modelname=get_extjs_modelname(restfulmodelcls),
                                            #modelitems=json.dumps(_get_extjs_modelfields(restfulmodelcls)))

def restfulmodelcls_to_extjsformitems(restfulmodelcls):
    return json.dumps(_get_extjs_modelfields(restfulmodelcls), indent=2)
