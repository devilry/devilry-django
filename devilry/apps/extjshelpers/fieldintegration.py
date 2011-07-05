from django.db.models import fields


def field_to_extjstype(field, fieldname):
    """ Convert django field to extjs  field type. """
    if isinstance(field, fields.IntegerField):
        return 'int'
    elif isinstance(field, fields.AutoField):
        return 'int'
    else:
        return 'string'
