#from django.db.models import fields
from django.db.models.fields.related import ForeignKey
from storeintegration import restfulmodelcls_to_extjsstore

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
        store = restfulmodelcls_to_extjsstore(foreignkey_restfulcls, integrateModel=True)
        return """
                xtype: 'combobox',
                valueField: 'id',
                displayField: 'short_name',
                listConfig: {{
                    loadingText: 'Searching...',
                    emptyText: 'No matching posts found.',

                    getInnerTpl: function() {{
                        return '{as_foreignkey_listconfig_tpl}'
                    }}
                }},
                store: {store}""".format(store=store,
                                         as_foreignkey_listconfig_tpl=foreignkey_restfulcls._meta.as_foreignkey_listconfig_tpl)
    else:
        return "xtype: 'textfield'"


def djangofield_to_extjsformfield(model, fieldname, foreignkey_restfulcls):
    if "__" in fieldname:
        fieldname = fieldname.split('__')[0]
    field = model._meta.get_field_by_name(fieldname)[0]

    #if isinstance(field, field.AutoField):
        #return None
    #else:
    xtype = djangofield_to_extjs_xtype(field, foreignkey_restfulcls)
    extfield = '{{ name: "{fieldname}", fieldLabel: "{field.verbose_name}", '\
            '{xtype} }}'.format(fieldname=fieldname, field=field,
                                    xtype=xtype)
    return extfield
