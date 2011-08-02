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
        '<strong>Short name</strong> is a short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).</p>',
    ]
});
