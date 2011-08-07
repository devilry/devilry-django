from storeintegration import restfulcls_to_extjsstore


def restfulcls_to_extjscombobox_xtype(restfulcls):
    store = restfulcls_to_extjsstore(restfulcls,
                                     integrateModel=True,
                                     modelkwargs=dict(result_fieldgroups=restfulcls._extjsmodelmeta.combobox_fieldgroups),
                                     storeidsuffix='Combo')
    listconfig = """listConfig: {{
                loadingText: 'Loading...',
                emptyText: 'No matching items found.',
                getInnerTpl: function() {{
                    return '{combobox_tpl}'
                }}
            }},""".format(combobox_tpl=restfulcls._extjsmodelmeta.combobox_tpl)

    model = restfulcls._meta.simplified._meta.model
    return """
            xtype: 'combobox',
            valueField: '{pkfieldname}',
            displayField: '{combobox_displayfield}',
            {listconfig}
            store: {store}""".format(store=store,
                                     listconfig=listconfig,
                                     combobox_displayfield=restfulcls._extjsmodelmeta.combobox_displayfield,
                                     pkfieldname=model._meta.pk.name)


def restfulcls_to_extjscombobox(restfulcls):
    return """Ext.create('Ext.form.field.ComboBox', {{
            {content}
        }});""".format(content=restfulcls_to_extjscombobox_xtype(restfulcls))
