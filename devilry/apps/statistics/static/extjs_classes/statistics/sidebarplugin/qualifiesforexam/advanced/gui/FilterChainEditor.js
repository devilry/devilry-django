Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.FilterChainEditor', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-filterchaineditor',
    hideHeaders: true,

    config: {
        filterchain: undefined,
        assignment_store: undefined
    },

    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.FilterEditor'
    ],

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.store = Ext.create('Ext.data.ArrayStore', {
            autoDestroy: true,
            idIndex: 0,
            fields: ['filters']
        });
        this._syncStoreWithLabel();

        Ext.apply(this, {
            title: Ext.String.format('Label: {0}', this.filterchain.label),
            columns: [{
                header: 'Filters', dataIndex: 'filter', flex: 1,
                renderer: function(filter, p, record) {
                    return filter.toReadableSummary(this.assignment_store);
                }
            }],
            tbar: [{
                xtype: 'button',
                text: 'Add filter',
                iconCls: 'icon-add-16',
                listeners: {
                    scope: this,
                    click: this._onClickAddFilter
                }
            }]
        });
        this.callParent(arguments);
    },

    _syncStoreWithLabel: function() {
        this.store.removeAll();
        Ext.defer(function() {
            Ext.each(this.filterchain.filters, function(filter, index) {
                this.store.add({
                    filter: filter
                });
            }, this);
        }, 200, this);
    },

    _onClickAddFilter: function() {
        var win = Ext.widget('window', {
            layout: 'fit',
            modal: true,
            width: 600,
            height: 400,
            items: {
                xtype: 'statistics-filtereditor',
                assignment_store: this.assignment_store,
                listeners: {
                    scope: this,
                    addFilter: function(filter) {
                        win.close();
                        this._onAddFilter(filter);
                    }
                }
            }
        });
        win.show();
    },

    _onAddFilter: function(filter) {
        console.log('Filter', filter);
        this.filterchain.filters.push(filter);
        //console.log(this.filterchain);
        this._syncStoreWithLabel();
    }
});
