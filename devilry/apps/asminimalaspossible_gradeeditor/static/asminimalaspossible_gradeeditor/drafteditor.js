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
            var staticfeedbackeditor = this.up('staticfeedbackeditor');
            staticfeedbackeditor.loadFeedbackViewer();
        }
    }, {
        text: 'Publish feedback',
        handler: function() {
            if (this.up('form').getForm().isValid()) {
                var staticfeedbackeditor = this.up('staticfeedbackeditor');

                var approved = Ext.getCmp('approved-checkbox').getValue();
                var staticfeedback = Ext.create('devilry.apps.gradeeditors.simplified.administrator.SimplifiedFeedbackDraft', {
                    draft: Ext.JSON.encode(approved),
                    published: true,
                    delivery: staticfeedbackeditor.deliveryid
                });

                staticfeedback.save({
                    success: function(response) {
                        console.log("Success");
                        console.log(response.data);
                        staticfeedbackeditor.loadFeedbackViewer()
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
