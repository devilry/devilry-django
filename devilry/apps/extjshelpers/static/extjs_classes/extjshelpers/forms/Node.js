Ext.define('devilry.extjshelpers.forms.Node', {
    extend: 'Ext.form.Panel',
    alias: 'widget.nodeform',
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
        fieldLabel: "Short name",
        xtype: 'textfield'
    }, {
        name: "long_name",
        fieldLabel: "Long name",
        xtype: 'textfield'
    }, {
        name: "parentnode",
        fieldLabel: "Parent",
        xtype: 'foreignkeyselector',
        model: 'devilry.extjshelpers.models.Node',
        emptyText: 'Select a parent node, or leave blank for no parent',
        displayTpl: '{long_name} ({short_name})',
        dropdownTpl: '<div class="important">{short_name}</div><div class="unimportant">{long_name}</div>',
        allowEmpty: true
    }],

    help: '<p><strong>Short name</strong> is a short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).</p>' +
        '<p><strong>Long name</strong> is a longer descriptive name which can contain any character.</p>' +
        '<p><strong>Parent</strong> is empty if this is a top-level node.</p>'
});
