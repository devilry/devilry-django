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
        height: 490
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
        margins: '0 0 10 0'
    },


    items: [{
        name: "short_name",
        fieldLabel: "Short name",
        xtype: 'textfield',
        emptyText: 'Example: firstassignment'
    }, {
        name: "long_name",
        fieldLabel: "Long name",
        xtype: 'textfield',
        emptyText: 'Example: Obligatory assignment 1'
    }, {
        name: "parentnode",
        fieldLabel: "Period",
        xtype: 'foreignkeyselector',
        model: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
        emptyText: 'Select a period',
        displayTpl: '{long_name} ({parentnode__short_name}.{short_name})',
        dropdownTpl: '<div class="important">{parentnode__short_name}.{short_name}</div>'+
            '<div class="unimportant">{parentnode__long_name}</div>' +
            '<div class="unimportant">{long_name}</div>'
    }, {
        name: "publishing_time",
        fieldLabel: "Publishing time",
        xtype: 'devilrydatetimefield',
        value: new Date()
    }, {
        name: "delivery_types",
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
        fieldLabel: "Anonymous?",
        xtype: 'checkbox'
    }],

    help: [
        {state: 'new', text: 'Set up the mandatory properties of an assignment. Further customization is available after you create the assignment.'},
        '<strong>Short name</strong> is a short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).',
        '<strong>Long name</strong> is a longer descriptive name which can contain any character.',
        'You must choose the <strong>period</strong> where this period belongs. A period is normally a semester.',
        'The <strong>publishing time</strong> is the time when students will be able to start adding deliveries on the assignment.',
        'If you only use Devilry to give feedback, but students deliver through an alternative channel, change <strong>how students add deliveries</strong>. This can also be used if the students deliver through an alternative electronic system such as <em>email</em>.',
        'If you check <strong>anonymous</strong>, examiners see a <em>candidate-id</em> instead of a username. A candidate-id must be set for each student.' //Normally students can see who their examiner is, however when <em>anonymous</em> is checked students do not get any information about their examiner(s).'
    ]
});
