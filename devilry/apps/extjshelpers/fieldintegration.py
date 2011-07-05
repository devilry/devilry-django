#from django.db.models import fields
from django.db.models.fields.related import ForeignKey
from storeintegration import restfulmodelcls_to_extjsstore
import jsdump



#def find_foreign_field(model, path):
    #fieldname = path.pop(0)
    #field = model._meta.get_field_by_name(fieldname)[0]
    #if isinstance(field, ForeignKey):
        #model = field.related.parent_model
        #return find_foreign_field(model, path)
    #else:
        #return field


def djangofield_to_extjs_xtype(djangofield, foreignkey_restfulcls):
    #print djangofield
    if isinstance(djangofield, ForeignKey):
        return dict(xtype = 'combobox',
                    store = jsdump.UnString(restfulmodelcls_to_extjsstore(foreignkey_restfulcls)))
    else:
        return dict(xtype='textfield')
    #return dict(xtype='textfield')


def djangofield_to_extjsformfield(model, fieldname, foreignkey_restfulcls):
    if "__" in fieldname:
        fieldname = fieldname.split('__')[0]
    field = model._meta.get_field_by_name(fieldname)[0]

    #if isinstance(field, field.AutoField):
        #return None
    #else:
    extfield = djangofield_to_extjs_xtype(field, foreignkey_restfulcls)
    extfield.update(dict(name = fieldname,
                         fieldLabel = field.verbose_name))
    return extfield
