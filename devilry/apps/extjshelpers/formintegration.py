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
    """
    Create a list of form items on the ExtJS xtype list format.
    These form items are generated from ``editablefields`` in the :ref:`Simplified
    class <simplified>` which the given ``restfulcls`` contains.

    ``editablefields`` is documented in :ref:`devilry.simplified.simplified_modelapi`.
    """
    js = '[\n    {0}\n]'.format(',\n    '.join(_iter_editfields(restfulcls)))
    return js

def restfulcls_to_foreignkeylist(restfulcls):
    """
    Generate a a javascript list of foreign-key field names, or an empty list
    if no ``foreignkey_fields`` is specified in the restfulcls.

    Foreign-key fields are found in ``restfulcls._meta.foreignkey_fields``,
    which is documented in :func:`devilry.restful.restful_modelapi`.
    """
    if hasattr(restfulcls._meta, 'foreignkey_fields'):
        foreignkeys = restfulcls._meta.foreignkey_fields.keys()
    else:
        foreignkeys = []
    return json.dumps(foreignkeys)
