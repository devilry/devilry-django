Ext.define('devilry.statistics.dataview.DataView', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-dataview',
    layout: 'fit',

    requires: [
        'devilry.statistics.dataview.SelectViewCombo',
        'devilry.statistics.dataview.MinimalGridView',
        'devilry.statistics.dataview.FullGridView'
    ],
    
    config: {
        loader: undefined,
        availableViews: [{
            clsname: 'devilry.statistics.dataview.FullGridView',
            label: 'Detailed view'
        }, {
            clsname: 'devilry.statistics.dataview.MinimalGridView',
            label: 'Minimal view'
        }],
        defaultViewClsname: 'devilry.statistics.dataview.FullGridView'
    },
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        var selectViewStore = Ext.create('Ext.data.Store', {
            fields: ['clsname', 'label'],
            data: this.availableViews,
            proxy: 'memory'
        });
        Ext.apply(this, {
            tbar: ['->', {
                xtype: 'statistics-dataview-selectviewcombo',
                availableViews: this.availableViews,
                defaultViewClsname: this.defaultViewClsname,
                listeners: {
                    scope: this,
                    selectView: this._setView
                }
            }]
        });
        this.callParent(arguments);
        this._setView(this.defaultViewClsname);
    },

    _setView: function(clsname) {
        this.removeAll();
        this._layout = Ext.create(clsname, {
            loader: this.loader
        });
        this.add(this._layout);
    },

    refresh: function() {
        this._layout.refresh();
    }
});
