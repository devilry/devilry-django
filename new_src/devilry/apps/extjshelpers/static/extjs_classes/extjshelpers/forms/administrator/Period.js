Ext.define('devilry.extjshelpers.forms.administrator.Period', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_periodform',
    cls: 'widget-periodform',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeySelector',
        'devilry.extjshelpers.formfields.DateTimeField'
    ],

    suggested_windowsize: {
        width: 700,
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
        margin: '0 0 10 0'
    },


    items: [{
        name: "short_name",
        fieldLabel: gettext("Short name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': spring01'
    }, {
        name: "long_name",
        fieldLabel: gettext("Long name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': Spring 2001'
    }, {
        name: "parentnode",
        fieldLabel: gettext("Subject"),
        xtype: 'foreignkeyselector',
        model: 'devilry.apps.administrator.simplified.SimplifiedSubject',
        emptyText: interpolate(gettext('Select a %(subject_term)s'), {
            subject_term: gettext('subject')
        }, true),
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
            fieldLabel: gettext("Start"),
            xtype: 'devilrydatetimefield',
            flex: 1
        }, {
            xtype: 'box',
            width: 20
        }, {
            name: "end_time",
            fieldLabel: gettext("End"),
            xtype: 'devilrydatetimefield',
            flex: 1
        }]
    }],

    help: [
        '<strong>' + gettext('Short name') + ':</strong> ' + gettext('A short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).'),
        '<strong>' + gettext('Long name') + ':</strong> ' + gettext('A longer descriptive name which can contain any character.')
    ]
});
