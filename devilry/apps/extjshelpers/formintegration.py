import json

from fieldintegration import djangofield_to_extjsformfield


def _iter_editfields(restfulcls):
    fieldnames = restfulcls.EditForm.Meta.fields
    for fieldname in fieldnames:
        foreignkey_restfulcls = restfulcls._meta.get_foreignkey_fieldcls(fieldname)
        extfield = djangofield_to_extjsformfield(restfulcls._meta.simplified._meta.model,
                                                 fieldname,
                                                 foreignkey_restfulcls)
        yield extfield

def restfulcls_to_extjsformitems(restfulcls):
    js = '[\n    {0}\n]'.format(',\n    '.join(_iter_editfields(restfulcls)))
    return js

def restfulcls_to_foreignkeylist(restfulcls):
    if hasattr(restfulcls._meta, 'foreignkey_fields'):
        foreignkeys = restfulcls._meta.foreignkey_fields.keys()
    else:
        foreignkeys = []
    return json.dumps(foreignkeys)
