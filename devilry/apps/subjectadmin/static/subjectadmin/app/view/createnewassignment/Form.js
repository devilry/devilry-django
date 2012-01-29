Ext.define('subjectadmin.view.createnewassignment.Form', {
    extend: 'Ext.form.Panel',
    alias: 'widget.createnewassignmentform',
    cls: 'createnewassignmentform form-stacked',
    requires: [
        'Ext.form.field.ComboBox',
        'Ext.form.field.Text',
        'Ext.form.field.Hidden',
        'Ext.toolbar.Toolbar',
        'devilry.extjshelpers.formfields.DateTimeField',
        'themebase.CreateButton',
        'themebase.AlertMessageList',
        'themebase.form.Help',
    ],
    ui: 'transparentpanel',

    fieldDefaults: {
        labelAlign: 'top'
    },
    defaults: {
        margin: {top: 20}
    },

    items: [{
        margin: {top: 0, bottom: 20},
        xtype: 'alertmessagelist'
    }, {
        margin: {top: 0},
        name: "long_name",
        fieldLabel: "Name",
        xtype: 'textfield',
        emptyText: 'Example: Obligatory assignment 1',
        allowBlank: false,
        width: 400
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.long_name.help')

    // How do students add deliveries
    }, {
        name: "delivery_types",
        flex: 1,
        fieldLabel: "How do students add deliveries?",
        xtype: 'combobox',
        queryMode: 'local',
        valueField: 'value',
        displayField: 'label',
        forceSelection: true,
        editable: false,
        width: 400,
        value: 0,
        store: Ext.create('Ext.data.Store', {
            fields: ['value', 'label'],
            data : [
                {value:0, label:"Electronically using Devilry"},
                {value:1, label:"Non-electronic (hand in on paper, oral examination, ...)"}
            ]
        })
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.delivery_types.help')

    // Short name
    }, {
        name: "short_name",
        fieldLabel: "Short name",
        xtype: 'textfield',
        allowBlank: false,
        emptyText: 'Example: assignment1'
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.short_name.help')

    // Publishing time
    }, {
        name: "publishing_time",
        fieldLabel: "Publishing time",
        xtype: 'devilrydatetimefield',
        allowBlank: false,
        value: new Date()
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.publishing_time.help')

    // Anonymous?
    }, {
        name: "anonymous",
        flex: 1,
        fieldLabel: "Anonymous?",
        xtype: 'combobox',
        queryMode: 'local',
        valueField: 'value',
        displayField: 'label',
        forceSelection: true,
        editable: false,
        value: false,
        store: Ext.create('Ext.data.Store', {
            fields: ['value', 'label'],
            data : [
                {value:false, label:"No"},
                {value:true, label:"Yes"}
            ]
        })
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.anonymous.help')

    }, {
        xtype: 'hiddenfield',
        name: 'scale_points_percent',
        value: 100
    }],

    dockedItems: [{
        xtype: 'toolbar',
        dock: 'bottom',
        ui: 'footer',
        padding: 0,
        items: [{
            xtype: 'createbutton',
            margin: {top: 10},
            formBind: true, //only enabled once the form is valid
            disabled: true
        }]
    }]
});
