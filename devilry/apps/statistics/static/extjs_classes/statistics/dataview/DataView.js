Ext.define('devilry.statistics.dataview.DataView', {
    extend: 'Ext.container.Container',
    alias: 'widget.statistics-dataview',
    layout: 'fit',

    requires: [
        'devilry.statistics.dataview.LayoutBase'
    ],
    
    config: {
        loader: undefined,
        layoutCls: undefined
    },
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        this.callParent(arguments);
        this.setView('devilry.statistics.dataview.LayoutBase');
    },

    setView: function(path) {
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
