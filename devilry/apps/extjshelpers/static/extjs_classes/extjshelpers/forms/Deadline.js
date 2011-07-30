Ext.define('devilry.extjshelpers.forms.Deadline', {
    extend: 'Ext.form.Panel',
    alias: 'widget.deadlineform',
    cls: 'widget-deadlineform',

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
        xtype: 'datefield',
        flex: 0,
        format: 'Y-m-d H:i:s',
    }, {
        name: "text",
        fieldLabel: "Text",
        flex: 1,
        xtype: 'textarea',
    }],


    help: '<p><strong>Choose a deadline</strong>. Students will be able to deliver after the ' +
        'deadline expires, however deliveries after the deadline will be clearly ' +
        'marked.</p>' +
        '<p>The <strong>text</strong> is displayed to students when they view the deadline, ' +
        'and when they add deliveries on the deadline.</p>'
});
