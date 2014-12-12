Ext.define('devilry.extjshelpers.forms.administrator.Subject', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_subjectform',
    cls: 'widget-periodform',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeySelector'
    ],

    suggested_windowsize: {
        width: 600,
        height: 400
    },

    flex: 8,

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
        name: "short_name",
        fieldLabel: gettext("Short name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': math101'
    }, {
        name: "long_name",
        fieldLabel: "Long name",
        xtype: 'textfield',
        emptyText: gettext('Example') + ': MATH101 - Introduction to mathematics'
    }, {
        name: "parentnode",
        fieldLabel: gettext("Node"),
        xtype: 'foreignkeyselector',
        model: 'devilry.apps.administrator.simplified.SimplifiedNode',
        emptyText: interpolate(gettext('Select a %(node_term)s'), {
            node_term: gettext('node')
        }, true),
        displayTpl: '{long_name} ({short_name})',
        dropdownTpl: '<div class="important">{short_name}</div><div class="unimportant">{long_name}</div>'
    }],

    help: [
        '<strong>' + gettext('Short name') + ':</strong> ' + gettext('A short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).'),
        '<strong>' + gettext('Long name') + ':</strong> ' + gettext('A longer descriptive name which can contain any character.')
    ]
});
