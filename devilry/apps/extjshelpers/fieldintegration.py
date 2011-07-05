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
        fkmeta = foreignkey_restfulcls._meta
        store = restfulmodelcls_to_extjsstore(foreignkey_restfulcls,
                                              integrateModel=True,
                                              modelkwargs=dict(result_fieldgroups=fkmeta.combobox_fieldgroups))
        listconfig = """listConfig: {{
                loadingText: 'Loading...',
                emptyText: 'No matching items found.',
                getInnerTpl: function() {{
                    return '{combobox_tpl}'
                }}
            }},""".format(combobox_tpl=fkmeta.combobox_tpl)

        return """
                xtype: 'combobox',
                valueField: '{pkfieldname}',
                displayField: '{combobox_displayfield}',
                {listconfig}
                store: {store}""".format(store=store,
                                         listconfig=listconfig,
                                         combobox_displayfield=fkmeta.combobox_displayfield,
                                         pkfieldname=fkmeta.simplified._meta.model._meta.pk.name)
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
