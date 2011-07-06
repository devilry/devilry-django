from modelintegration import get_extjs_modelname, restfulcls_to_extjsmodel

def restfulcls_to_extjsstore(restfulcls, integrateModel=False, modelkwargs={}):
    if integrateModel:
        model = restfulcls_to_extjsmodel(restfulcls)
    else:
        model = "'{modelname}'".format(modelname=get_extjs_modelname(restfulcls, **modelkwargs))
    return """Ext.create('Ext.data.Store', {{
            model: {model},
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        }})""".format(model=model)
