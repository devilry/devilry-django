[{
    xtype: 'form',
    border: false,
    items: [{
        xtype: 'checkboxfield',
        boxLabel: 'Approved',
        id: 'approved-checkbox'
    }],

    buttons: [{
        text: 'Cancel',
        handler: function() {
            var gradeeditor = this.up('gradeeditor');
            gradeeditor.exit();
        }
    }, {
        text: 'Publish feedback',
        handler: function() {
            if (this.up('form').getForm().isValid()) {
                var gradeeditor = this.up('gradeeditor');

                var approved = Ext.getCmp('approved-checkbox').getValue();
                var staticfeedback = Ext.create('devilry.apps.gradeeditors.simplified.administrator.SimplifiedFeedbackDraft', {
                    draft: Ext.JSON.encode(approved),
                    published: true,
                    delivery: gradeeditor.deliveryid
                });

                staticfeedback.save({
                    success: function(response) {
                        console.log("Success");
                        console.log(response.data);
                        gradeeditor.exit();
                    },
                    failure: function(response) {
                        console.log("Error!");
                        console.log(response);
                    }
                });
            }
        }
    }]
}]
