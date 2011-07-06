def extjs_restful_modelapi(cls):
    """
    Checks for, and adds defaults for the extjs specific inner meta class, ExtjsModelMeta.
    """
    if not hasattr(cls, "ExtjsModelMeta"):
        class ExtjsModelMeta:
            """ Fake javascript-meta class """
        cls.ExtjsModelMeta = ExtjsModelMeta
    cls._exjsmodelmeta = cls.ExtjsModelMeta
    if not hasattr(cls._exjsmodelmeta, 'combobox_displayfield'):
        cls._exjsmodelmeta.combobox_displayfield = 'id'
    if not hasattr(cls._exjsmodelmeta, 'combobox_fieldgroups'):
        cls._exjsmodelmeta.combobox_fieldgroups = {}
    if not hasattr(cls._exjsmodelmeta, 'combobox_tpl'):
        cls._exjsmodelmeta.combobox_tpl = '{' + cls._exjsmodelmeta.combobox_displayfield + '}'

    return cls
