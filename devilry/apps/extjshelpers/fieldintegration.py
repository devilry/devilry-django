#from django.db.models import fields
from django.db.models.fields.related import ForeignKey
from django.db.models import fields
from comboboxintegration import restfulcls_to_extjscombobox_xtype
from datepickerintegration import restfulcls_to_datepicker_xtype

#def find_foreign_field(model, path):
    #fieldname = path.pop(0)
    #field = model._meta.get_field_by_name(fieldname)[0]
    #if isinstance(field, ForeignKey):
        #model = field.related.parent_model
        #return find_foreign_field(model, path)
    #else:
        #return field


def djangofield_to_extjs_xtype(djangofield, foreignkey_restfulcls):
    if isinstance(djangofield, ForeignKey):
        return restfulcls_to_extjscombobox_xtype(foreignkey_restfulcls)
    elif isinstance(djangofield, fields.DateTimeField):
        return restfulcls_to_datepicker_xtype()
    elif isinstance(djangofield, fields.BooleanField):
        return "xtype: 'checkbox'"
    else:
        return "xtype: 'textfield'"


def djangofield_to_extjsformfield(model, fieldname, foreignkey_restfulcls):
    field = model._meta.get_field_by_name(fieldname)[0] #!!! INTERNAL DJANGO
    xtype = djangofield_to_extjs_xtype(field, foreignkey_restfulcls)
    extfield = '{{ name: "{fieldname}", fieldLabel: "{field.verbose_name}", '\
            '{xtype} }}'.format(fieldname=fieldname, field=field,
                                    xtype=xtype)
    return extfield
