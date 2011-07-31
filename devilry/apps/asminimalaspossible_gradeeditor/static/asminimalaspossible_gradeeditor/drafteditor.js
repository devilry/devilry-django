{
    xtype: 'form',
    border: false,
    items: [{
        xtype: 'checkboxfield',
        boxLabel: 'Approved',
        id: 'approved-checkbox'
    }],

    buttons: [{
        text: 'Close',
        handler: function() {
            var gradeeditor = this.up('gradeeditor');
            gradeeditor.exit();
        }
    }, {
        text: 'Publish feedback',
        handler: function() {
            if (this.up('form').getForm().isValid()) {
                var approved = Ext.getCmp('approved-checkbox').getValue();
                var draft = Ext.JSON.encode(approved);

                var gradeeditor = this.up('gradeeditor');
                gradeeditor.saveDraftAndPublish(draft);
            }
        }
    }]
}
