Ext.define('devilry.statistics.dataview.DataView', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-dataview',
    layout: 'fit',

    requires: [
        'devilry.statistics.dataview.SelectViewCombo',
        'devilry.statistics.dataview.MinimalGridView',
        'devilry.statistics.ClearFilters',
        'devilry.statistics.ScalePointsPanel',
        'devilry.statistics.dataview.FullGridView'
    ],

    titleTpl: Ext.create('Ext.XTemplate',
        '{parentnode__long_name:ellipsis(60)} &mdash; {long_name}'
    ),
    
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
            title: this.titleTpl.apply(this.loader.periodRecord.data),
            tbar: [{
                xtype: 'statistics-clearfilters',
                loader: this.loader
            }, {
                xtype: 'button',
                text: 'Scale assignments',
                listeners: {
                    scope: this,
                    click: this._onScaleAssignments
                }
            }, '->', {
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
    },

    getSelectedStudents: function() {
        return this._layout.getSelectedStudents();
    },

    _onScaleAssignments: function() {
        Ext.widget('window', {
            width: 400,
            height: 400,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'statistics-scalepointspanel',
                store: this.loader.assignment_store
            }
        }).show();
    }
});
