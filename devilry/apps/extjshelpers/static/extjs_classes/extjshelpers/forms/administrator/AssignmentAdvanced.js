Ext.define('devilry.extjshelpers.forms.administrator.AssignmentAdvanced', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_assignmentadvancedform',
    cls: 'widget-assignmentadvancedform',

    suggested_windowsize: {
        width: 600,
        height: 450
    },

    flex: 4,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },
    defaults: {
        margins: '0 0 10 0'
    },

    items: [{
        name: "must_pass",
        fieldLabel: "Must pass?",
        xtype: 'checkbox',
        checked: true
    }, {
        name: "attempts",
        fieldLabel: "Attempts",
        xtype: 'textfield'
    }, {
        name: "anonymous",
        fieldLabel: "Anonymous?",
        xtype: 'checkbox'
    }],

    help: [
        '<strong>TODO:</strong> Integrate this view into the grade configuration?'
    ]
});
