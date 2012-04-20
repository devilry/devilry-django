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
        xtype: 'box',
        cls: 'metainfo bootstrap',
        itemId: 'metainfo',
        html: ''
    }, {
        margin: {top: 20, bottom: 20},
        xtype: 'alertmessagelist'

    // Long name
    }, {
        name: "long_name",
        fieldLabel: dtranslate('subjectadmin.assignment.long_name.label'),
        xtype: 'textfield',
        emptyText: dtranslate('subjectadmin.assignment.long_name.example'),
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
        emptyText: dtranslate('subjectadmin.assignment.short_name.example'),
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.short_name.help')

    // How do students add deliveries
    }, {
        xtype: 'radiogroup',
        fieldLabel: dtranslate('subjectadmin.assignment.delivery_types.label'),
        vertical: true,
        itemId: 'deliveryTypesRadioGroup',
        cls: 'delivery_types-radiogroup',
        columns: 1,
        items: [{
            boxLabel: dtranslate('subjectadmin.assignment.delivery_types.electronic'),
            name: 'delivery_types',
            inputValue: 0,
            checked: true
        }, {
            boxLabel: dtranslate('subjectadmin.assignment.delivery_types.nonelectronic'),
            name: 'delivery_types',
            inputValue: 1
        }]

    // First deadline
    }, {
        xtype: 'themebase-datetimefield',
        name: 'first_deadline',
        width: 300,
        fieldLabel: dtranslate('subjectadmin.assignment.first_deadline.label')
    }, {
        xtype: 'formhelp',
        itemId: 'first_deadline-help',
        margin: {top: 5},
        html: dtranslate('subjectadmin.assignment.first_deadline.help')

    }, {
        xtype: 'fieldset',
        title: dtranslate('themebase.advanced_options'),
        cls: 'advanced_options_fieldset',
        collapsible: true,
        collapsed: true,
        padding: 10,
        defaults: {
            margin: {top: 20}
        },
        items: [{
        // Anonymous?
            xtype: 'checkboxfield',
            margin: {top: 0},
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

        // Add all related students
        }, {
            xtype: 'checkboxfield',
            name:'add_all_relatedstudents',
            margin: {top: 20},
            boxLabel: dtranslate('subjectadmin.assignment.add_all_relatedstudents.label'),
            checked: true,
            labelAlign: 'left'
        }, {
            xtype: 'formhelp',
            margin: {bottom: 10},
            html: dtranslate('subjectadmin.assignment.add_all_relatedstudents.help')

        // Autosetup examiners
        }, {
            xtype: 'checkboxfield',
            margin: {top: 20},
            name: 'autosetup_examiners',
            checked: true,
            labelAlign: 'left',
            boxLabel: dtranslate('subjectadmin.assignment.autosetup_examiners.label')
        }, {
            xtype: 'formhelp',
            itemId: 'autosetup_examiners-help',
            margin: {top: 5},
            html: dtranslate('subjectadmin.assignment.autosetup_examiners.help')
        }]
    }],

    dockedItems: [{
        xtype: 'toolbar',
        dock: 'bottom',
        ui: 'footer',
        padding: 0,
        margin: {top: 15},
        items: [{
            xtype: 'createbutton',
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
