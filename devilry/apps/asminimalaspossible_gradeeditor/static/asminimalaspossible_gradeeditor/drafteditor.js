{
    xtype: 'form',
    border: false,
    items: [{
        xtype: 'checkboxfield',
        boxLabel: 'Approved',
        id: 'approved-checkbox'
    }],

    buttons: [{
        text: 'Publish feedback',
        handler: function() {
            if (this.up('form').getForm().isValid()) {
                var approved = Ext.getCmp('approved-checkbox').getValue();
                var draft = Ext.JSON.encode(approved);

                var gradedrafteditor = this.up('gradedrafteditor');
                gradedrafteditor.saveDraftAndPublish(draft);
            }
        }
    }]
}
