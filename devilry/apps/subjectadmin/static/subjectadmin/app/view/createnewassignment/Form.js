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

    layout: 'anchor',

    fieldDefaults: {
        labelAlign: 'top',
        //labelStyle: 'font-weight:bold'
    },
    defaults: {
        margin: {top: 20},
        anchor:'50%'
    },


    items: [{
        xtype: 'container',
        anchor: '100%',
        layout: 'anchor',
        defaults: {anchor:'100%'},
        items: [{
            xtype: 'container',
            layout: 'column',
            items: [{
                name: "long_name",
                fieldLabel: "Long name",
                xtype: 'textfield',
                columnWidth: .7,
                margin: {right: 40},
                emptyText: 'Example: Obligatory assignment 1'
            }, {
                name: "short_name",
                columnWidth: .3,
                fieldLabel: "Short name",
                xtype: 'textfield',
                emptyText: 'Example: firstassignment'
            }]
        }, {
            xtype: 'formhelp',
            html: [
                'Choose the name of the assignment. Short name is ',
                'used when the long name takes to much space. Short name can ',
                'only contain english lower-case letters, numbers and underscore (_).'
            ].join('')
        }]
    }, {
        xtype: 'container',
        anchor: '100%',
        layout: 'column',
        items: [{
            xtype: 'container',
            layout: 'anchor',
            defaults: {anchor:'100%'},
            columnWidth: .5,
            margin: {right: 40},
            defaults: {
                margin: {bottom: 20},
                anchor:'100%'
            },
            items: [{
                name: "publishing_time",
                fieldLabel: "Publishing time",
                xtype: 'devilrydatetimefield',
                value: new Date()
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
                value: 0,
                store: Ext.create('Ext.data.Store', {
                    fields: ['value', 'label'],
                    data : [
                        {value:0, label:"Electronically using Devilry"},
                        {value:1, label:"Non-electronic (hand in on paper, oral examination, ...)"}
                    ]
                })
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
            }]
        }, {
            xtype: 'box',
            html: '', // Should put something here
            columnWidth: .5
        }]
    }, {
        xtype: 'hiddenfield',
        name: 'scale_points_percent',
        value: 100
    }]
});
