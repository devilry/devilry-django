Ext.define('devilry.extjshelpers.forms.Deadline', {
    extend: 'Ext.form.Panel',
    alias: 'widget.deadlineform',
    cls: 'widget-deadlineform',
    requires: [
        'devilry.extjshelpers.formfields.DateTimeField'
    ],

    flex: 10,

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
    }, {
        name: "text",
        fieldLabel: "Text",
        flex: 1,
        xtype: 'textarea',
    }],


    help: [
        '<strong>Choose a deadline</strong>. Students will be able to deliver after the deadline expires, however deliveries after the deadline will be clearly marked.',
        'The <strong>text</strong> is displayed to students when they view the deadline, and when they add deliveries on the deadline.'
    ]
});
