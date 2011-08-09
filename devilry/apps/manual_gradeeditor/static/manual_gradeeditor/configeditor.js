{
    xtype: 'form',
    border: false,
    items: [{
        xtype: 'checkboxfield',
        boxLabel: 'Default value',
        id: 'defaultvalue'
    }, {
        xtype: 'textarea',
        fieldLabel: 'Field label',
        id: 'fieldlabel'
    }],

    buttons: [{
        text: 'Save',
        handler: function() {
            if (this.up('form').getForm().isValid()) {
                var defaultvalue = Ext.getCmp('defaultvalue').getValue();
                var fieldlabel = Ext.getCmp('fieldlabel').getValue();
                var config = Ext.JSON.encode({
                    defaultvalue: defaultvalue,
                    fieldlabel: fieldlabel
                });

                var configeditor = this.up('configeditor');
                configeditor.saveConfig(config);
            }
        }
    }]
}
