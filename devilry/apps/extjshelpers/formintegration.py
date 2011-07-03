from modelintegration import get_extjs_modelname

def get_extjs_modelfields(restfulmodelcls):
    modelitems = """{
            fieldLabel: 'short_name',
            name: 'short'
        },{
            fieldLabel: 'long_name',
            name: 'long'
        }"""

def restfulmodelcls_to_extjsstore(restfulmodelcls):    
    return """Ext.create('Ext.form.Panel, {
                  renderTo: 'form_example',
                  title: 'test',
                  model: '{modelname}',
                  items: [{modelitems}]
                  }""".format(modelname=get_extjs_modelname(restfulmodelcls) \
                                  modelitems=get_extjs_modelfields(restfulmodelcls))    
