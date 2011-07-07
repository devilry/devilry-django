from fieldintegration import djangofield_to_extjsformfield

def _iter_editfields(restfulmodelcls):
    for fieldname in restfulmodelcls._meta.simplified._meta.resultfields.aslist():
        extfield = djangofield_to_extjsformfield(restfulmodelcls._meta.simplified._meta.model,
                                                 fieldname,
                                                 restfulmodelcls._meta.get_foreignkey_fieldcls(fieldname))
        yield extfield

def restfulmodelcls_to_extjsformitems(restfulmodelcls):
    js = '[\n    {0}\n]'.format(',\n    '.join(_iter_editfields(restfulmodelcls)))
    #print js
    return js
