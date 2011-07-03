from modelintegration import get_extjs_modelname
#from fieldintegration import field_to_extjstype
import json

def _iter_search_fields(simplifiedcls):
    meta = simplifiedcls._meta
    for fieldname in meta.searchfields.aslist():
        yield fieldname

def get_extjs_modelfields(restfulmodelcls):
    modelitems = [dict(fieldLabel=fieldname, name=fieldname) \
            for fieldname in _iter_search_fields(restfulmodelcls._meta.simplified)]
    return modelitems

def restfulmodelcls_to_extjsforms(restfulmodelcls):
    return """model: '{modelname}',
              items: {modelitems}""".format(modelname=get_extjs_modelname(restfulmodelcls),
                                            modelitems=json.dumps(get_extjs_modelfields(restfulmodelcls)))
