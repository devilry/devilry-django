from modelintegration import get_extjs_modelname, restfulcls_to_extjsmodel

def restfulcls_to_extjsstore(restfulcls, integrateModel=False, modelkwargs={},
                            pagesize=None):
    if integrateModel:
        model = restfulcls_to_extjsmodel(restfulcls, **modelkwargs)
    else:
        model = "'{modelname}'".format(modelname=get_extjs_modelname(restfulcls))
    if pagesize:
        jspagesize = ' pageSize: {0},'.format(pagesize)
    else:
        jspagesize = ''
    return """Ext.create('Ext.data.Store', {{
            model: {model},
            remoteFilter: true,
            remoteSort: true,{jspagesize}
            autoSync: true
        }})""".format(model=model, jspagesize=jspagesize)
