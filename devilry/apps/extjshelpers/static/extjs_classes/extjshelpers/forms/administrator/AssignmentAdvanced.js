Ext.define('devilry.extjshelpers.forms.administrator.AssignmentAdvanced', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_assignmentadvancedform',
    cls: 'widget-assignmentadvancedform',

    suggested_windowsize: {
        width: 650,
        height: 450
    },

    flex: 6,

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
        fieldLabel: 'Must pass?',
        //boxLabel: "Check this if the student is required to pass this this subject?",
        xtype: 'checkbox',
        checked: true
    }, {
        name: "anonymous",
        fieldLabel: "Anonymous?",
        xtype: 'checkbox'
    }, {
        name: "delivery_types",
        fieldLabel: "How to students add deliveries?",
        xtype: 'combobox',
        queryMode: 'local',
        valueField: 'value',
        displayField: 'label',
        forceSelection: true,
        editable: false,
        store: Ext.create('Ext.data.Store', {
            fields: ['value', 'label'],
            data : [
                {value:0, label:"Electronically using devilry"},
                {value:1, label:"Non-electronic (hand in on paper, oral examination, ...)"}
            ]
        })
    }],

    help: [
        'If you check <strong>must pass</strong>, any student registered on a group on this assignment is <em>required</em> to pass this assignment to get a passing grade on this period.',
        'If you check <strong>anonymous</strong>, examiners see a <em>candidate-id</em> instead of a username. A candidate-id must be set for each student. Normally students can see who their examiner is, however when <em>anonymous</em> is checked students do not get any information about their examiner(s).'
    ]
});
