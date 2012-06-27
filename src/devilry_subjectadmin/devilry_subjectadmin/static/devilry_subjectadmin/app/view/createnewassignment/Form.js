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
        fieldLabel: gettext('Long name'),
        xtype: 'textfield',
        emptyText: gettext('Example of assignment long name'),
        allowBlank: false,
        width: 400
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: gettext('Choose a descriptive name for your assignment.')

    // Short name
    }, {
        name: "short_name",
        fieldLabel: gettext('Short name'),
        xtype: 'textfield',
        allowBlank: false,
        emptyText: gettext('assignment-shortname-example'),
    }, {
        xtype: 'formhelp',
        margin: {top: 5},
        html: gettext("Choose a short name with at most 20 letters for your assignment. Can only contain lowercase english letters (<em>a-z</em>), <em>numbers</em>, <em>'_'</em> and <em>'-'</em>. This is used the the regular name takes to much space.")

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
        margin: {top: 5},
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
        margin: {top: 5},
        html: gettext('The default deadline added to each student when adding new students to the assignment.')

    }, {
        xtype: 'fieldset',
        title: gettext('Advanced options'),
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
            boxLabel: gettext('Anonymous?')
        }, {
            xtype: 'formhelp',
            margin: {top: 5},
            html: gettext('For <strong>exams</strong>, this should normally be <em>checked</em>. If an assignment is anonymous, examiners see a candidate-id instead of a username. A candidate-id <strong>must</strong> be set for each student.')

        // Publishing time
        }, {
            xtype: 'devilry_extjsextras-datetimefield',
            width: 300,
            fieldLabel: gettext('Publishing time'),
            name: "publishing_time",
            value: new Date()
        }, {
            xtype: 'formhelp',
            margin: {top: 5},
            html: gettext('Choose a time when time when students will be able to start adding deliveries on the assignment. The default is to publish assignment when creating the assignment. Note that students must be registered on the assignment as well before they can add any deliveries.')

        // Add all related students
        }, {
            xtype: 'checkboxfield',
            name:'add_all_relatedstudents',
            margin: {top: 20},
            boxLabel: gettext('Add all students to this assignment?'),
            checked: true,
            labelAlign: 'left'
        }, {
            xtype: 'formhelp',
            margin: {bottom: 10},
            html: gettext('If this option is selected, all students registered on the period will automatically be added to the assignment when it is created.')

        // Autosetup examiners
        }, {
            xtype: 'checkboxfield',
            margin: {top: 20},
            name: 'autosetup_examiners',
            checked: true,
            labelAlign: 'left',
            boxLabel: gettext('Automatically setup examiners?')
        }, {
            xtype: 'formhelp',
            itemId: 'autosetup_examiners-help',
            margin: {top: 5},
            html: gettext('Automatically setup examiners on this assignment by matching tags on examiners and students registered on the period.')
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
        var cssclasses = 'devilry_subjectadmin_createnewassignmentform';
        if(this.cls) {
            cssclasses += ' ' + this.cls;
        }
        this.cls = cssclasses;
        this.callParent(arguments);
    }
});
