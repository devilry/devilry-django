Ext.define('devilry.statistics.dataview.DataView', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-dataview',
    layout: 'fit',

    requires: [
        'devilry.statistics.dataview.MinimalGridView',
        'devilry.statistics.dataview.FullGridView'
    ],
    
    config: {
        loader: undefined,
        defaultView: 'devilry.statistics.dataview.FullGridView'
    },
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        var selectViewStore = Ext.create('Ext.data.Store', {
            fields: ['path', 'label'],
            data: [{
                path: 'devilry.statistics.dataview.MinimalGridView',
                label: 'Minimal view'
            }, {
                path: 'devilry.statistics.dataview.FullGridView',
                label: 'Detailed view'
            }],
            proxy: 'memory'
        });
        Ext.apply(this, {
            tbar: ['->', {
                xtype: 'combobox',
                valueField: 'path',
                displayField: 'label',
                forceSelection: true,
                store: selectViewStore,
                value: this.defaultView,
                listeners: {
                    scope: this,
                    select: this._onSelectView
                }
            }]
        });
        this.callParent(arguments);
        this._setView(this.defaultView);
    },

    _onSelectView: function(combo, records) {
        var record = records[0];
        this._setView(record.get('path'));
    },

    _setView: function(path) {
        this.removeAll();
        this._layout = Ext.create(path, {
            loader: this.loader
        });
        this.add(this._layout);
    },

    refresh: function() {
        this._layout.refresh();
    }
});
