Ext.define('devilry.extjshelpers.forms.administrator.AssignmentAdvanced', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_assignmentadvancedform',
    cls: 'widget-assignmentadvancedform',

    suggested_windowsize: {
        width: 650,
        height: 450
    },

    flex: 2.5,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    //fieldDefaults: {
        //labelAlign: 'top',
        //labelWidth: 100,
        //labelStyle: 'font-weight:bold'
    //},
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
        name: "attempts",
        fieldLabel: "Attempts",
        xtype: 'textfield'
    }],

    help: [
        'If you check <strong>must pass</strong>, any student registered on a group on this assignment is <em>required</em> to pass this assignment to get a passing grade on this period.',
        'If you check <strong>anonymous</strong>, examiners see a <em>candidate-id</em> instead of a username. A candidate-id must be set for each student. Normally students can see who their examiner is, however when <em>anonymous</em> is checked students do not get any information about their examiner(s).',
        'When <strong>attempts</strong> is set to something other than <em>0</em>, examiners is asked to create new deadlines for students as long as they have failed to get a passing grade <em>attempts</em> times. When a student has failed to get a passing grade <em>attempts</em> times, their group is automatically closed, which means they get a failing grade on the assignment.',
        'Note that <strong>attempts</strong> is just a hint ment to make the job of the examiner easier. Examiners can re-open closed groups if needed, and they can manually close groups even when they have not failed <em>attempts</em> times.'
    ]
});
