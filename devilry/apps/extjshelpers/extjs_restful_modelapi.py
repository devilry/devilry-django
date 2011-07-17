def extjs_restful_modelapi(cls):
    """
    Decorator for RESTful classes.

    Checks for, and adds defaults for the extjs specific inner meta class, ExtjsModelMeta.

    ExtjsModelMeta can have the following attributes:

        combobox_displayfield
            When this object is used in a combobox (search, foreign-key, ...),
            the combobox need a field, ``displayField``, to show after the an item has been
            selected (when not showing a dropdown). This attribute species
            a field name in the resultdata from
            :meth:`devilry.simplified.SimplifiedModelApi.search` to use as
            ``displayField`` for comboboxes. Defaults to ``'id'``.
        combobox_fieldgroups
            Species the ``result_fieldgroups`` to send to
            :meth:`devilry.simplified.SimplifiedModelApi.search` when querying
            for data in a combobox (see combobox_displayfield for more details
            on comboboxes). Defaults to an empty list.
        combobox_tpl
            Species the ``Ext.XTemplate`` (an extjs class) template to use for each item in
            the combobox dropdown (see ``combobox_displayfield`` parameter for more details
            on comboboxes). Defaults to ``'{combobox_displayfield}'``.
    """
    if not hasattr(cls, "ExtjsModelMeta"):
        class ExtjsModelMeta:
            """ Fake javascript-meta class """
        cls.ExtjsModelMeta = ExtjsModelMeta
    cls._extjsmodelmeta = cls.ExtjsModelMeta
    if not hasattr(cls._extjsmodelmeta, 'combobox_displayfield'):
        cls._extjsmodelmeta.combobox_displayfield = 'id'
    if not hasattr(cls._extjsmodelmeta, 'combobox_fieldgroups'):
        cls._extjsmodelmeta.combobox_fieldgroups = []
    if not hasattr(cls._extjsmodelmeta, 'combobox_tpl'):
        cls._extjsmodelmeta.combobox_tpl = '{' + cls._extjsmodelmeta.combobox_displayfield + '}'

    return cls
