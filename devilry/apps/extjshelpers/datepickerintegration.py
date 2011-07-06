from storeintegration import restfulmodelcls_to_extjsstore

#TODO get restfulcls and fetch default date values
def restfulcls_to_datepicker_xtype():
    return """xtype: 'datefield', 
              format: 'Y-m-d H:i:s'
              """
