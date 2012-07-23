Ext.define('devilry_subjectadmin.view.createnewassignment.Form', {
    extend: 'Ext.form.Panel',
    alias: 'widget.createnewassignmentform',
    requires: [
        'Ext.form.field.ComboBox',
        'Ext.form.field.Text',
        'Ext.form.field.Hidden',
        'Ext.toolbar.Toolbar',
        //'devilry_extjsextras.form.DateField',
        //'devilry_extjsextras.form.TimeField',
        'devilry_extjsextras.form.DateTimeField',
        'devilry_extjsextras.CreateButton',
        'devilry_extjsextras.AlertMessageList',
        'devilry_extjsextras.form.Help',
    ],
    ui: 'transparentpanel',

    fieldDefaults: {
        labelAlign: 'top',
        labelStyle: 'font-weight: bold'
    },
    defaults: {
        margin: '20 0 0 0'
    },

    items: [{
        margin: '0 0 20 0',
        xtype: 'box',
        cls: 'metainfo bootstrap',
        itemId: 'metainfo',
        html: ''
    }, {
        margin: '20 0 20 0',
        xtype: 'alertmessagelist'

    // Long name
    }, {
        xtype: 'container',
        layout: 'column',
        items: [{
            columnWidth: 0.7,
            name: "long_name",
            fieldLabel: gettext('Long name'),
            xtype: 'textfield',
            emptyText: pgettext('createnewassignment', 'Example: Obligatory assignment one'),
            allowBlank: false,
            padding: '0 20 0 0'
        }, {
            name: "short_name",
            columnWidth: 0.3,
            fieldLabel: gettext('Short name'),
            xtype: 'textfield',
            allowBlank: false,
            emptyText: pgettext('createnewassignment', 'Example: oblig-1'),
        }]
    }, {
        xtype: 'formhelp',
        margin: '5 0 0 0',
        html: [
            gettext('Choose a long and a short name. Short name is used in places where long name takes too much space, such as table headers and navigation.'),
            gettext("The short name can have max 20 letters, and it can only contain lowercase english letters (<em>a-z</em>), <em>numbers</em>, <em>'_'</em> and <em>'-'</em>.")
        ]

    // How do students add deliveries
    }, {
        xtype: 'radiogroup',
        fieldLabel: gettext('How do students add deliveries?'),
        vertical: true,
        itemId: 'deliveryTypesRadioGroup',
        cls: 'delivery_types-radiogroup',
        columns: 1,
        items: [{
            boxLabel: gettext('Using Devilry'),
            name: 'delivery_types',
            inputValue: 0,
            checked: true
        }, {
            boxLabel: gettext('Not using Devilry'),
            name: 'delivery_types',
            inputValue: 1
        }]
    }, {
        xtype: 'formhelp',
        margin: '5 0 0 0',
        html: gettext('If you only use Devilry to give feedback, and students deliver paper copies or through an alternative channel (oral presentation, email, ...), choose <em>Not using Devilry</em>.')

    // First deadline
    }, {
        xtype: 'devilry_extjsextras-datetimefield',
        cls: 'first_deadline',
        name: 'first_deadline',
        width: 300,
        fieldLabel: gettext('First deadline')
    }, {
        xtype: 'formhelp',
        itemId: 'first_deadline-help',
        margin: '5 0 0 0',
        html: gettext('The default deadline added to each student when adding new students to the assignment.')

    }, {
        xtype: 'fieldset',
        title: gettext('Advanced options (click to expand)'),
        //cls: 'advanced_options_fieldset',
        collapsible: true,
        collapsed: true,
        titleCollapse: true,
        padding: 20,
        defaults: {
            margin: '20 0 0 0'
        },
        items: [{
        // Anonymous?
            xtype: 'checkboxfield',
            margin: '0 0 0 0',
            name: 'anonymous',
            labelAlign: 'left',
            boxLabel: gettext('Anonymous?')
        }, {
            xtype: 'formhelp',
            margin: '5 0 0 0',
            html: gettext('For exams, this should normally be checked. If an assignment is anonymous, examiners see candidate-id instead of any personal information about the students.')

        // Publishing time
        }, {
            xtype: 'devilry_extjsextras-datetimefield',
            width: 300,
            fieldLabel: gettext('Publishing time'),
            name: "publishing_time",
            value: new Date()
        }, {
            xtype: 'formhelp',
            margin: '5 0 0 0',
            html: gettext('Choose a time when time when students will be able to start adding deliveries on the assignment. The default is to publish assignment when creating the assignment. Note that students must be registered on the assignment as well before they can add any deliveries.')

        // Add all related students
        }, {
            xtype: 'checkboxfield',
            name:'add_all_relatedstudents',
            margin: '20 0 0 0',
            boxLabel: gettext('Add all students to this assignment?'),
            checked: true,
            labelAlign: 'left'
        }, {
            xtype: 'formhelp',
            margin: '0 0 10 0',
            html: gettext('If this option is selected, all students registered on the period will automatically be added to the assignment when it is created.')

        // Autosetup examiners
        }, {
            xtype: 'checkboxfield',
            margin: '20 0 0 0',
            name: 'autosetup_examiners',
            checked: true,
            labelAlign: 'left',
            boxLabel: gettext('Automatically setup examiners?')
        }, {
            xtype: 'formhelp',
            itemId: 'autosetup_examiners-help',
            margin: '5 0 0 0',
            html: gettext('Automatically setup examiners on this assignment by matching tags on examiners and students registered on the period.')
        }]
    }],

    dockedItems: [{
        xtype: 'toolbar',
        dock: 'bottom',
        ui: 'footer',
        padding: 0,
        margin: '15 0 0 0',
        items: [{
            xtype: 'createbutton',
            formBind: true, //only enabled once the form is valid
            disabled: true
        }]
    }],

    initComponent: function() {
        var cssclasses = 'devilry_subjectadmin_createnewassignmentform';
        if(this.cls) {
            cssclasses += ' ' + this.cls;
        }
        this.cls = cssclasses;
        this.callParent(arguments);
    }
});
