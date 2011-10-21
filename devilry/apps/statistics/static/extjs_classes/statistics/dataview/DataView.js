Ext.define('devilry.statistics.dataview.DataView', {
    extend: 'Ext.container.Container',
    alias: 'widget.statistics-dataview',
    layout: 'fit',

    requires: [
        'devilry.statistics.dataview.MinimalGridView',
        'devilry.statistics.dataview.FullGridView'
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
        this.setView('devilry.statistics.dataview.FullGridView');
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
