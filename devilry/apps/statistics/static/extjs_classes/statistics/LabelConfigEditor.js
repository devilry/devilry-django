Ext.define('devilry.statistics.LabelConfigEditor', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-labelconfigeditor',
    hideHeaders: true,

    config: {
        label: undefined,
        assignment_store: undefined
    },

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
            title: Ext.String.format('Label: {0}', this.label.label),
            columns: [{
                header: 'Filters', dataIndex: 'filter', flex: 1,
                renderer: function(filter, p, record) {
                    return filter.toString(this.assignment_store);
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
            Ext.each(this.label.filters, function(filter, index) {
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
            width: 800,
            height: 600,
            items: {
                xtype: 'statistics-filtereditor',
                assignment_store: this.assignment_store,
                listeners: {
                    scope: this,
                    save: function(filter) {
                        win.close();
                        this._onSaveFilter(filter);
                    }
                }
            }
        });
        win.show();
    },

    _onSaveFilter: function(filter) {
        console.log(filter);
        this.label.filters.push(filter);
        this._syncStoreWithLabel();
    }
});
