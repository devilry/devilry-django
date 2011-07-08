from fieldintegration import djangofield_to_extjsformfield

def _iter_editfields(restfulcls):
    for fieldname in restfulcls._meta.simplified._meta.resultfields.aslist():
        extfield = djangofield_to_extjsformfield(restfulcls._meta.simplified._meta.model,
                                                 fieldname,
                                                 restfulcls._meta.get_foreignkey_fieldcls(fieldname))
        yield extfield

def restfulcls_to_extjsformitems(restfulcls):
    js = '[\n    {0}\n]'.format(',\n    '.join(_iter_editfields(restfulcls)))
    #print js
    return js
