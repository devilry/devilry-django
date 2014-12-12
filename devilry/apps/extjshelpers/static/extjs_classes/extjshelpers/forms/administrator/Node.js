Ext.define('devilry.extjshelpers.forms.administrator.Node', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_nodeform',
    cls: 'widget-nodeform',
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
        emptyText: gettext('Example') + ': mathfaculty'
    }, {
        name: "long_name",
        fieldLabel: gettext("Long name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': Faculty of Mathematics'
    }, {
        name: "parentnode",
        fieldLabel: gettext("Parent"),
        xtype: 'foreignkeyselector',
        model: 'devilry.apps.administrator.simplified.SimplifiedNode',
        emptyText: gettext('Select a parent, or leave blank for no parent'),
        displayTpl: '{long_name} ({short_name})',
        dropdownTpl: '<div class="important">{short_name}</div><div class="unimportant">{long_name}</div>',
        allowEmpty: true
    }],

    help: [
        '<strong>' + gettext('Short name') + ':</strong> ' + gettext('A short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).'),
        '<strong>' + gettext('Long name') + ':</strong> ' + gettext('A longer descriptive name which can contain any character.'),
        '<strong>' + gettext('Parent') + ':</strong> ' + interpolate(gettext('Organize this %(node_term)s below another %(node_term)s. May be empty.'), {
            node_term: gettext('node')
        }, true)
    ]
});
