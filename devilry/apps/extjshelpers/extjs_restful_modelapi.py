def extjs_restful_modelapi(cls):
    """
    Checks for, and adds defaults for the extjs specific inner meta class, ExtjsModelMeta.

    ExtjsModelMeta can have the following attributes:

        combobox_displayfield
            When this object is used in a combobox (search, foreign-key, ...),
            the combobox need a field, ``displayField``, to show after the an item has been
            selected (when not showing a dropdown). This attribute species
            a field name from the result_fieldgroups to use as ``displayField``
            for comboboxes.
        combobox_fieldgroups
            Species the ``result_fieldgroups`` to use when querying for data in a
            combobox (see combobox_displayfield for more details on comboboxes).
        combobox_tpl
            Species the ``Ext.String.format`` template to use for each item in
            the combobox dropdown (see combobox_displayfield for more details
            on comboboxes).
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
