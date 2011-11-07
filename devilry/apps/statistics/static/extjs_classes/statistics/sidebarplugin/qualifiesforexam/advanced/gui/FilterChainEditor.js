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
        this.store = this.filterchain;

        Ext.apply(this, {
            columns: [{
                header: 'Filters', dataIndex: 'filter', flex: 1,
                renderer: function(filter, p, record) {
                    return filter.toReadableSummary(this.assignment_store);
                }
            }],
            tbar: [this.removeButton = Ext.widget('button', {
                text: 'Remove',
                iconCls: 'icon-delete-16',
                disabled: true,
                listeners: {
                    scope: this,
                    click: this._onClickDelete
                }
            }), {
                xtype: 'button',
                text: 'Add',
                iconCls: 'icon-add-16',
                listeners: {
                    scope: this,
                    click: this._onClickAddFilter
                }
            }]
        });
        this.on('selectionchange', this._onSelectionChange, this);
        this.callParent(arguments);
    },

    _onSelectionChange: function(grid, selected) {
        if(selected.length === 0) {
            this.removeButton.disable();
        } else {
            this.removeButton.enable();
        }
    },

    _onClickDelete: function() {
        var selected = this.getSelectionModel().getSelection();
        if(selected.length != 1) {
            Ext.MessageBox.alert('Error', 'Please select a row from the list.');
            return;
        }
        var selectedItem = selected[0];
        this.store.remove(selectedItem);
    },

    _onClickAddFilter: function() {
        var win = Ext.widget('window', {
            layout: 'fit',
            title: 'Edit rule',
            onEsc: Ext.emptyFn,
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

    _onAddFilter: function(filterArgs) {
        this.filterchain.addFilter(filterArgs);
    }
});
