from modelintegration import get_extjs_modelname

def restfulmodelcls_to_extjsstore(restfulmodelcls):
    return """Ext.create('Ext.data.Store', {{
            model: '{modelname}',
            remoteFilter: true,
            remoteSort: true,
            autoLoad: true,
            autoSync: true
        }});""".format(modelname=get_extjs_modelname(restfulmodelcls))


def restfulmodelcls_to_extjsstore(restfulmodelcls):
    modelitems = []
    
    return """Ext.create('Ext.form.Panel, {
                  renderTo: 'form_example',
                  title: 'test',
                  model: '{modelname}',
                  items: [{modelitems}]
                  }""".format(modelname=get_extjs_modelname(restfulmodelcls) \
                                  modelitems=get_extjs_modelfields(restfulmodelcls))


                   
