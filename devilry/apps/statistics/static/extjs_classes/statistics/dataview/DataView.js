Ext.define('devilry.statistics.dataview.DataView', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-dataview',
    layout: 'fit',

    requires: [
        'devilry.extjshelpers.SearchField',
        'devilry.statistics.dataview.SelectViewCombo',
        'devilry.statistics.dataview.MinimalGridView',
        'devilry.statistics.ClearFilters',
        'devilry.statistics.ScalePointsPanel',
        'devilry.statistics.dataview.FullGridView'
    ],

    config: {
        loader: undefined,
        availableViews: [{
            clsname: 'devilry.statistics.dataview.MinimalGridView',
            label: 'Minimal view'
        }, {
            clsname: 'devilry.statistics.dataview.FullGridView',
            label: 'Detailed view'
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
            tbar: [{
                xtype: 'searchfield',
                width: 250,
                emptyText: 'Search...',
                listeners: {
                    scope: this,
                    newSearchValue: this._search,
                    emptyInput: function() { this._search() }
                }
            }, {
                xtype: 'button',
                text: 'x',
                listeners: {
                    scope: this,
                    click: function() { this._search() }
                }
            }, '->', {
                xtype: 'statistics-clearfilters',
                loader: this.loader,
                listeners: {
                    scope: this,
                    filterClearedPressed: function() {
                        this.down('searchfield').setValue('');
                    }
                }
            }, {
                xtype: 'button',
                text: 'Change weight of assignments',
                listeners: {
                    scope: this,
                    click: this._onScaleAssignments
                }
            }, {
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

    _search: function(input) {
        if(input) {
            this.loader.clearFilter();
            this.loader.filterBy('Search for: ' + input, function(record) {
                var username = record.get('username') || '';
                var full_name = record.get('full_name') || '';
                return username.search(input) != -1 || full_name.search(input) != -1;
            }, this);
        } else {
            this.loader.clearFilter();
        }
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

    _onScaleAssignments: function(button) {
        Ext.widget('window', {
            width: 350,
            height: 250,
            title: button.text,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'statistics-scalepointspanel',
                store: this.loader.assignment_store,
                loader: this.loader
            }
        }).show();
    }
});
