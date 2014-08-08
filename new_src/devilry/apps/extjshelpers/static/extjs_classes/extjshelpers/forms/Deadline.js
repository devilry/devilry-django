Ext.define('devilry.extjshelpers.forms.Deadline', {
    extend: 'Ext.form.Panel',
    alias: 'widget.deadlineform',
    cls: 'widget-deadlineform',
    requires: [
        'devilry.extjshelpers.formfields.DateTimeField'
    ],

    flex: 6,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },

    items: [{
        name: "deadline",
        fieldLabel: 'Deadline',
        xtype: 'devilrydatetimefield',
        flex: 0,
        allowBlank: false
    }, {
        name: "text",
        fieldLabel: "Text",
        flex: 1,
        height: 250,
        xtype: 'textarea'
    }],


    help: [
        '<strong>Choose a deadline</strong>. Students will be able to deliver after the deadline expires, however deliveries after the deadline will be clearly marked.',
        'The <strong>text</strong> is displayed to students when they view the deadline, and when they add deliveries on the deadline. The text is shown exactly as you see it in the text-box. No formatting of any kind is applied.',
        '<strong>NOTE:</strong> Examiners can not move Deadlines. We are planning a major cleanup of the Examiner UI, which will include the ability to move deadlines. In the meantime, ask your course administrator to move deadlines if needed.'
    ]
});
