Ext.define('devilry.gradeeditors.GradeEditorSelectForm', {
    extend: 'Ext.form.Panel',
    alias: 'widget.gradeeditorselectform',
    cls: 'widget-gradeeditorselectform',
    requires: ['devilry.gradeeditors.GradeEditorSelector'],

    suggested_windowsize: {
        width: 900,
        height: 600
    },

    flex: 0.8,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },

    items: [{
        name: 'gradeeditorid',
        fieldLabel: "Select a grade editor",
        xtype: 'gradeeditorselector'
    }],

    help: [
        'A <strong>grade editor</strong> is what examiners use to give feedback to students.',

        'Internally in Devilry, a grade is:<ul>' +
        '   <li>The number of points. Any grade in Devilry is represented as a number, however this number is mainly for statistical purposes.</li>' +
        '   <li>A very short text that students view. Usually something like: <em>Approved</em>, <em>B</em> or <em>7/10</em>.</li>' +
        '   <li>A longer text that students can view.</li>' +
        '</ul>',

        'To make it easy for examiners to create all the information related to a <em>grade</em>, ' +
        'Devilry use <em>grade editors</em>. Grade editors give examiners a unified user-' +
        'interface tailored for different kinds of grading systems.'
    ]
});
