Ext.define('subjectadmin.view.createnewassignment.Form', {
    extend: 'Ext.form.Panel',
    alias: 'widget.createnewassignmentform',
    requires: [
        'Ext.form.field.ComboBox',
        'Ext.form.field.Text',
        'Ext.form.field.Hidden',
        'Ext.toolbar.Toolbar',
        //'themebase.form.DateField',
        //'themebase.form.TimeField',
        'themebase.form.DateTimeField',
        'themebase.CreateButton',
        'themebase.AlertMessageList',
        'themebase.form.Help',
    ],
    ui: 'transparentpanel',

    fieldDefaults: {
        labelAlign: 'top',
        labelStyle: 'font-weight: bold'
    },
    defaults: {
        margin: {top: 20}
    },

    items: [{
        margin: {top: 0, bottom: 20},
        xtype: 'alertmessagelist'

    // Long name
    }, {
        margin: {top: 0},
        name: "long_name",
        fieldLabel: dtranslate('subjectadmin.assignment.long_name.label'),
        xtype: 'textfield',
        emptyText: 'Example: Obligatory assignment 1',
        allowBlank: false,
        width: 400
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.long_name.help')

    // Short name
    }, {
        name: "short_name",
        fieldLabel: dtranslate('subjectadmin.assignment.short_name.label'),
        xtype: 'textfield',
        allowBlank: false,
        emptyText: 'Example: assignment1'
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.short_name.help')

    // How do students add deliveries
    }, {
        name: "delivery_types",
        flex: 1,
        fieldLabel: dtranslate('subjectadmin.assignment.delivery_types.label'),
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
                {value:0, label: dtranslate('subjectadmin.assignment.delivery_types.electronic')},
                {value:1, label: dtranslate('subjectadmin.assignment.delivery_types.nonelectronic')}
            ]
        })
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.delivery_types.help')

    // Anonymous?
    }, {
        xtype: 'checkboxfield',
        margin: {top: 20},
        name: 'anonymous',
        labelAlign: 'left',
        boxLabel: dtranslate('subjectadmin.assignment.anonymous.label')
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.anonymous.help')

    // Publishing time
    }, {
        xtype: 'themebase-datetimefield',
        width: 300,
        fieldLabel: dtranslate('subjectadmin.assignment.publishing_time.label'),
        name: "publishing_time",
        value: new Date()
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.publishing_time.help')

    }, {
        xtype: 'fieldset',
        title: dtranslate('subjectadmin.assignment.add_all_relatedstudents.label'),
        collapsible: true,
        //collapsed: true,
        checkboxToggle: true,
        checkboxName:'add_all_relatedstudents',
        padding: 10,
        items: [{

        // Autosetup examiners
            xtype: 'themebase-datetimefield',
            name: 'first_deadline',
            width: 300,
            fieldLabel: dtranslate('subjectadmin.assignment.first_deadline.label')
        }, {
            xtype: 'formhelp',
            margin: {top: 5},
            html: dtranslate('subjectadmin.assignment.first_deadline.help')

        // Autosetup examiners
        }, {
            xtype: 'checkboxfield',
            margin: {top: 20},
            name: 'autosetup_examiners',
            labelAlign: 'left',
            boxLabel: dtranslate('subjectadmin.assignment.autosetup_examiners.label')
        }, {
            xtype: 'formhelp',
            margin: {top: 5},
            html: dtranslate('subjectadmin.assignment.autosetup_examiners.help')
        }]
    }],

    dockedItems: [{
        xtype: 'toolbar',
        dock: 'bottom',
        ui: 'footer',
        padding: 0,
        items: [{
            xtype: 'createbutton',
            margin: {top: 20},
            formBind: true, //only enabled once the form is valid
            disabled: true
        }]
    }],

    initComponent: function() {
        var cssclasses = 'createnewassignmentform';
        if(this.cls) {
            cssclasses += ' ' + this.cls;
        }
        this.cls = cssclasses;
        this.callParent(arguments);
    }
});
