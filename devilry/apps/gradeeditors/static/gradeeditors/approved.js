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
            var staticfeedbackeditableinfo = this.up('staticfeedbackeditableinfo');
            staticfeedbackeditableinfo.loadFeedbackViewer();
        }
    }, {
        text: 'Publish feedback',
        handler: function() {
            if (this.up('form').getForm().isValid()) {
                var staticfeedbackeditableinfo = this.up('staticfeedbackeditableinfo');

                var approved = Ext.getCmp('approved-checkbox').getValue();
                var feedbacktext = Ext.getCmp('feedback-text').getValue();

                var staticfeedback = Ext.create('devilry.apps.examiner.simplified.SimplifiedStaticFeedback', {
                    grade: approved? "Approved": "Not approved",
                    is_passing_grade: approved,
                    points: approved? 1: 0,
                    rendered_view: Ext.String.format('<pre>{0}</pre>', feedbacktext),
                    delivery: staticfeedbackeditableinfo.deliveryid
                });

                staticfeedback.save({
                    success: function(response) {
                        console.log("Success");
                        console.log(response.data);
                        staticfeedbackeditableinfo.loadFeedbackViewer()
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
