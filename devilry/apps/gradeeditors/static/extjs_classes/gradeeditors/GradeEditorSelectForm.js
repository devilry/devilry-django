Ext.define('devilry.gradeeditors.GradeEditorSelectForm', {
    extend: 'Ext.form.Panel',
    alias: 'widget.gradeeditorselectform',
    cls: 'widget-gradeeditorselectform',
    requires: ['devilry.gradeeditors.GradeEditorSelector'],

    suggested_windowsize: {
        width: 600,
        height: 400
    },

    flex: 10,

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
        fieldLabel: "Grade editor",
        xtype: 'gradeeditorselector'
    }],

    help: [
        'A <strong>grade editor</strong> is what examiners use to give feedback to students.</p>',
        'Internally in Devilry, a grade is:<ul><li>The number of points</li><li>TODO</li>TODO</li></ul>'
    ]
});
