class OneToMany(object):
    def __init__(self, related_field, fields=[]):
        self.related_field = related_field
        self.fields = fields

    def as_list(self, instance):
        relatedfield = getattr(instance, self.related_field)
        qry = relatedfield.values(*self.fields)
        return [x for x in qry]

def _is_local_field(fieldname):
    return not isinstance(fieldname, OneToMany) and not '__' in fieldname

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

    def all_aslist(self):
        """
        Get all fields in always_available_fields and in additional_fieldgroups.
        """
        return self.aslist(fieldgroups=self.additional_aslist())

    def iterfieldnames(self):
        """
        Iterate over all fieldnames in this FieldSpec.
        """
        return self.all_aslist().__iter__()

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
                if _is_local_field(fieldname)]

    def localfieldgroups_aslist(self):
        """ Get all fieldgroups containing fields belonging to the current table.

        Fields not belonging to the current table are any field
        containing ``__``. """
        local_fieldgroups = []
        for fieldgroup, fieldnames in self.additional_fieldgroups.iteritems():
            for fieldname in fieldnames:
                if _is_local_field(fieldname):
                    local_fieldgroups.append(fieldname)
                    break
        return local_fieldgroups

    def __add__(self, other):
        """
        Adds two FieldSpec instances to a new FieldSpec instance.
        Raises an error if any values are already defined
        """
        new_fields = []
        new_fieldgroups = {}

        # copy the self's fields first
        for val in self.always_available_fields:
            if val in new_fields:
                raise ValueError("%s already in always_available_fields" % val)
            new_fields.append(val)

        # then copy the others' fields
        for val in other.always_available_fields:
            if val in new_fields:
                raise ValueError("%s already in always_available_fields" % val)
            new_fields.append(val)

        # then self's field_groups
        for key, val in self.additional_fieldgroups.items():
            new_fieldgroups[key] = []
            for v in val:
                if v in new_fieldgroups[key]:
                    raise ValueError("%s already in additional_fieldgroups['%s']" % (v, key))
                new_fieldgroups[key].append(v)

        # then self's field_groups
        for key, val in other.additional_fieldgroups.items():
            if not key in new_fieldgroups:
                new_fieldgroups[key] = []
            for v in val:
                if v in new_fieldgroups[key]:
                    raise ValueError("%s already in additional_fieldgroups['%s']" % (v, key))
                new_fieldgroups[key].append(v)

        return FieldSpec(*new_fields, **new_fieldgroups)
