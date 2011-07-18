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
            height: 400
        }]
    }],

    buttons: [{
        text: 'Publish feedback',
        handler: function() {
            if (this.up('form').getForm().isValid()) {
                // In a real application, this would submit the form to the configured url
                // this.up('form').getForm().submit();
                //var feedback = this.up('examinerfeedback');
                var approved = Ext.getCmp('approved-checkbox').getValue();
                var feedbacktext = Ext.getCmp('feedback-text').getValue();
                var staticfeedback = Ext.create(feedbackeditorGlobals.staticfeedbackmodelname, {
                    grade: approved? "Approved": "Not approved",
                    is_passing_grade: approved,
                    points: approved? 1: 0,
                    rendered_view: Ext.String.format('<pre>{0}</pre>', feedbacktext),
                    delivery: feedbackeditorGlobals.deliveryid
                });
                staticfeedback.save({
                    success: function(response) {
                        console.log("Success");
                        console.log(response.data);
                    },
                    failure: function() {
                        console.log("Error!");
                    }
                });
            }
        }
    }]
}]
