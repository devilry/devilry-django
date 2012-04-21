[{
    xtype: 'form',
    border: false,
    items: [{
        xtype: 'checkboxfield',
        boxLabel: 'Approved',
        id: 'approved-checkbox'
    }, {
        xtype: 'panel',
        title: 'Feedback text',
        margin: {top: 20},
        layout: 'fit',
        items: [{
            xtype: 'textarea',
            id: 'feedback-text',
            width: 600,
            height: 300
        }]
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
                var feedbacktext = Ext.getCmp('feedback-text').getValue();

                var staticfeedback = Ext.create('devilry.apps.examiner.simplified.SimplifiedStaticFeedback', {
                    grade: approved? "Approved": "Not approved",
                    is_passing_grade: approved,
                    points: approved? 1: 0,
                    rendered_view: Ext.String.format('{0}', feedbacktext),
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
