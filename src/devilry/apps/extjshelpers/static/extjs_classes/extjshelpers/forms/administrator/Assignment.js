Ext.define('devilry.extjshelpers.forms.administrator.Assignment', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_assignmentform',
    cls: 'widget-assignmentform',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeySelector',
        'devilry.extjshelpers.formfields.DateTimeField'
    ],

    suggested_windowsize: {
        width: 850,
        height: 550
    },

    flex: 5,

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
        margin: '0 0 10 0'
    },


    items: [{
        name: "short_name",
        fieldLabel: gettext("Short name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': firstassignment'
    }, {
        name: "long_name",
        fieldLabel: gettext("Long name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': Obligatory assignment 1'
    }, {
        name: "parentnode",
        fieldLabel: gettext("Period"),
        xtype: 'foreignkeyselector',
        model: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
        emptyText: interpolate(gettext('Select a %(period_term)s'), {
            period_term: gettext('period')
        }, true),
        displayTpl: '{long_name} ({parentnode__short_name}.{short_name})',
        dropdownTpl: '<div class="important">{parentnode__short_name}.{short_name}</div>'+
            '<div class="unimportant">{parentnode__long_name}</div>' +
            '<div class="unimportant">{long_name}</div>'
    }, {
        name: "publishing_time",
        fieldLabel: gettext("Publishing time"),
        xtype: 'devilrydatetimefield',
        value: new Date()
    }, {
        name: "delivery_types",
        fieldLabel: gettext("How do students add deliveries?"),
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
                {value:0, label: gettext("Electronically using Devilry")},
                {value:1, label: gettext("Non-electronic (hand in on paper, oral examination, ...)")}
            ]
        })
    }, {
        name: "deadline_handling",
        fieldLabel: interpolate(gettext("How would you like to handle %(deadlines_term)s?"), {
            deadlines_term: gettext('deadlines')
        }, true),
        xtype: 'combobox',
        queryMode: 'local',
        valueField: 'value',
        displayField: 'label',
        forceSelection: true,
        editable: false,
        value: DevilrySettings.DEVILRY_DEFAULT_DEADLINE_HANDLING_METHOD,
        store: Ext.create('Ext.data.Store', {
            fields: ['value', 'label'],
            data : [
                {value:0, label: gettext("SOFT: Students can add deliveries after the deadline, but deliveries after the deadline are distinctly highlighted in the examiner and admin interfaces.")},
                {value:1, label: gettext("HARD: Students can not add deliveries after the deadline.")}
            ]
        })
    }, {
        name: "anonymous",
        fieldLabel: gettext("Anonymous?"),
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
                {value:false, label: gettext("No")},
                {value:true, label: gettext("Yes")}
            ]
        })
    }, {
        xtype: 'hiddenfield',
        name: 'scale_points_percent',
        value: 100
    }],

    help: [
        {state: 'new', text: gettext('Set up the mandatory properties of an assignment. Further customization is available after you create the assignment.')},
        '<strong>' + gettext('Short name') + ':</strong> ' + gettext('A short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).'),
        '<strong>' + gettext('Long name') + ':</strong> ' + gettext('A longer descriptive name which can contain any character.'),
        gettext('The <strong>publishing time</strong> is the time when students will be able to start adding deliveries on the assignment.'),
        gettext('If you only use Devilry to give feedback, but students deliver through an alternative channel, change <strong>how students add deliveries</strong>. This can also be used if the students deliver through an alternative electronic system such as <em>email</em>.'),
        gettext('If you set <strong>anonymous</strong> to <em>yes</em>, examiners see a <em>candidate-id</em> instead of a username. A candidate-id must be set for each student.')
    ]
});
