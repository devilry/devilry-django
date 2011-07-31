Ext.define('devilry.extjshelpers.formfields.ForeignKeyBrowser', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.foreignkeybrowser',
    showHeaders: false,
    border: false,

    config: {
        tpl: '{id}',
        model: 'devilry.extjshelpers.models.Node',
        foreignkeyselector: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var me = this;
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            remoteFilter: true,
            remoteSort: true,
            autoSync: true,
            autoLoad: true
        });

        Ext.apply(this, {
            dockedItems: [{
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: true
            }],

            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                renderer: function(value, metaData, record) {
                    return this.tpl.apply(record.data);
                }
            }],

            listeners: {
                scope: this,
                itemmouseup: this.onSelect
            }
        });
        this.callParent(arguments);
    },

    onSelect: function(grid, record) {
        this.foreignkeyselector.onSelect(record);
        this.up('window').close();
    }
});
