class FieldSpec(object):
    """
    Specifies and groups fields for search and read results.
    """
    def __init__(self, *always_available_fields, **additional_fieldgroups):
        """
        :param always_available_fields:
            Fields that is always available.
        :param additional_fieldgroups:
            Each key is the name of a fieldgroup, and the value is
            a list/tuple/iterable of field names.
        """
        self.always_available_fields = always_available_fields
        self.additional_fieldgroups = additional_fieldgroups


    def aslist(self, fieldgroups=None):
        """ Get the fields in ``always_available_fields`` and all
        fields in any of the ``fieldgroups``.

        :param fieldgroups:
            Tuple/list of fieldgroups. Fieldgroups are keys in
            ``additional_fieldgroups`` (see __init__).
        """
        if fieldgroups:
            fields = list(self.always_available_fields)
            for group in fieldgroups:
                fields.extend(self.additional_fieldgroups.get(group, []))
            return fields
        else:
            return self.always_available_fields

    def additional_aslist(self):
        """
        Returns a list of the keys in ``additional_fieldgroups``.
        """
        return list(self.additional_fieldgroups.keys())

    def localfields_aslist(self):
        """ Get all fields belonging to the current table.

        Fields not belonging to the current table are any field
        containing ``__``. """
        return [fieldname for fieldname in self.aslist(self.additional_aslist()) \
                if not '__' in fieldname]
