Ext.define('devilry.extjshelpers.forms.Node', {
    extend: 'Ext.form.Panel',
    alias: 'widget.nodeform',
    cls: 'widget-nodeform',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeySelector'
    ],

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

    help: '<p><strong>Choose a node</strong>. Students will be able to deliver after the node expires, however deliveries after the node will be clearly marked.</p><p>The <strong>text</strong> is displayed to students when they view the node, and when they add deliveries on the node.</p>',
});
