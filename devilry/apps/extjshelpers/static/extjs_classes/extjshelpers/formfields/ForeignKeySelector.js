Ext.define('devilry.extjshelpers.formfields.ForeignKeySelector', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.foreignkeyselector',
    requires: [
        'devilry.extjshelpers.models.Node'
    ],

    config: {
        valueField: 'id',
        displayField: 'id',
        dropdownTpl: '{id}'
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            store: Ext.create('Ext.data.Store', {
                model: 'devilry.extjshelpers.models.Node',
                remoteFilter: true,
                remoteSort: true,
                autoSync: true,
                autoLoad: true
            }),

            listConfig: {
                loadingText: 'Loading...',
                emptyText: 'No matching items found.',
                getInnerTpl: function() {
                    return me.dropdownTpl;
                }
            },
        });
        this.callParent(arguments);
    }
});
