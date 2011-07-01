from modelintegration import get_extjs_modelname

def restfulmodelcls_to_extjsstore(restfulmodelcls):
    return """Ext.create('Ext.data.Store', {{
            model: '{modelname}',
            remoteFilter: true,
            remoteSort: true,
            autoLoad: true,
            autoSync: true
        }});""".format(modelname=get_extjs_modelname(restfulmodelcls))
