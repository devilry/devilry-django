from modelintegration import get_extjs_modelname, restfulmodelcls_to_extjsmodel

def restfulmodelcls_to_extjsstore(restfulmodelcls, integrateModel=False, modelkwargs={}):
    if integrateModel:
        model = restfulmodelcls_to_extjsmodel(restfulmodelcls)
    else:
        model = "'{modelname}'".format(modelname=get_extjs_modelname(restfulmodelcls, **modelkwargs))
    return """Ext.create('Ext.data.Store', {{
            model: {model},
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        }})""".format(model=model)
