Ext.define('subjectadmin.view.createnewassignment.Form', {
    extend: 'Ext.form.Panel',
    alias: 'widget.createnewassignmentform',
    cls: 'createnewassignmentform form-stacked',
    requires: [
        //'devilry.extjshelpers.formfields.ForeignKeySelector',
        'devilry.extjshelpers.formfields.DateTimeField',
        'themebase.form.Help'
    ],
    ui: 'transparentpanel',

    //layout: 'anchor',

    fieldDefaults: {
        labelAlign: 'top',
        //labelStyle: 'font-weight:bold'
    },
    defaults: {
        margin: {top: 20},
        //anchor:'50%'
    },


    items: [{
        name: "long_name",
        fieldLabel: "Long name",
        xtype: 'textfield',
        emptyText: 'Example: Obligatory assignment 1',
        width: 400,
        height: 60
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: translate('subjectadmin.assignment.long_name.help')

    // How deliveries
    }, {
        name: "delivery_types",
        flex: 1,
        fieldLabel: "How to students add deliveries?",
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
        html: translate('subjectadmin.assignment.delivery_types.help')

    // Short name
    }, {
        name: "short_name",
        fieldLabel: "Short name",
        xtype: 'textfield',
        emptyText: 'Example: assignment1'
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: translate('subjectadmin.assignment.short_name.help')

    // Publishing time
    }, {
        name: "publishing_time",
        fieldLabel: "Publishing time",
        xtype: 'devilrydatetimefield',
        value: new Date()
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: translate('subjectadmin.assignment.publishing_time.help')

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
        html: translate('subjectadmin.assignment.anonymous.help')

    }, {
        xtype: 'hiddenfield',
        name: 'scale_points_percent',
        value: 100
    }]
});
