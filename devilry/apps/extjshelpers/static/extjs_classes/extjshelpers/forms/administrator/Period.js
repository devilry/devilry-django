Ext.define('devilry.extjshelpers.forms.administrator.Period', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_periodform',
    cls: 'widget-periodform',
    requires: ['devilry.extjshelpers.formfields.ForeignKeySelector'],

    suggested_windowsize: {
        width: 600,
        height: 500
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
    defaults: {
        margins: '0 0 10 0'
    },


    items: [{
        name: "short_name",
        fieldLabel: "Short name",
        xtype: 'textfield',
        emptyText: 'Example: spring01'
    }, {
        name: "long_name",
        fieldLabel: "Long name",
        xtype: 'textfield',
        emptyText: 'Example: Spring 2001'
    }, {
        name: "parentnode",
        fieldLabel: "Subject",
        xtype: 'foreignkeyselector',
        model: 'devilry.apps.administrator.simplified.SimplifiedSubject',
        emptyText: 'Select a parent subject',
        displayTpl: '{long_name} ({short_name})',
        dropdownTpl: '<div class="important">{short_name}</div><div class="unimportant">{long_name}</div>'
    }, {
        xtype: 'fieldcontainer',
        fieldLabel: 'Time span',
        //labelStyle: 'font-weight:bold;padding:0',
        layout: 'hbox',

        fieldDefaults: {
            labelAlign: 'top'
        },

        items: [{
            name: "start_time",
            fieldLabel: "Start",
            xtype: 'datefield',
            format: 'Y-m-d H:i:s',
            flex: 1,
            emptyText: 'YYYY-MM-DD hh:mm:ss'
        }, {
            xtype: 'box',
            width: 20
        }, {
            name: "end_time",
            fieldLabel: "End",
            xtype: 'datefield',
            format: 'Y-m-d H:i:s',
            flex: 1,
            emptyText: 'YYYY-MM-DD hh:mm:ss'
        }]
    }],

    help: '<p><strong>Short name</strong> is a short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).</p>' +
        '<p><strong>Long name</strong> is a longer descriptive name which can contain any character.</p>' +
        '<p><strong>Parent</strong> the subject where this period belongs.</p>'

});
