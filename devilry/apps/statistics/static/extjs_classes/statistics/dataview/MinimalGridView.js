Ext.define('devilry.statistics.dataview.MinimalGridView', {
    extend: 'devilry.statistics.dataview.BaseView',
    layout: 'fit',
    requires: [
        'devilry.extjshelpers.SortByLastnameColumn'
    ],

    labelTpl: Ext.create('Ext.XTemplate',
        '<ul class="labels-list">',
        '    <tpl for="labelKeys">',
        '       <li class="label-{.}">{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    getGridColumns: function() {
        var me = this;
        var gridColumns = [{
            header: 'Username', dataIndex: 'username',
            width: 100,
            locked: true
        }, {
            xtype: 'sortbylastnamecolumn',
            header: 'Full name', dataIndex: 'full_name',
            minWidth: 140,
            flex: 2
        }, {
            header: 'Labels', dataIndex: 'labelKeys',
            width: 150,
            renderer: function(value, p, record) {
                return me.labelTpl.apply(record.data);
            }
        }];
        return gridColumns;
    },

    refresh: function() {
        this.loadData();
    },

    loadData: function() {
        this.refreshView();
    },

    createGrid: function(extraOpts) {
        var gridColumns = this.getGridColumns();
        var gridOpts = Ext.apply({
            multiSelect: true,
            autoScroll: true,
            store: this.loader.store,
            columns: gridColumns,
            bbar: ['->', {
                xtype: 'tbtext',
                text: this._getTbText()
            }]
        });
        if(extraOpts) {
            Ext.apply(gridOpts, extraOpts);
        }
        this.mon(this.loader, 'filterCleared', this._onFilterChange, this);
        this.mon(this.loader, 'filterApplied', this._onFilterChange, this);
        var grid = Ext.widget('grid', gridOpts);
        return grid;
    },

    _getTbText: function() {
        return Ext.create('Ext.XTemplate', 
            'Showing {visible} of {total} students'
        ).apply({
            total: this.loader.totalStudents,
            visible: this.loader.store.data.items.length
        });
    },

    _onFilterChange: function() {
        this.down('tbtext').setText(this._getTbText());
    },

    createLayout: function() {
        this.add(this.createGrid());
    },

    refreshView: function() {
        this.removeAll();
        this.createLayout();
    },

    getSelectedStudents: function() {
        return this.grid.getSelectionModel().getSelection();
    }
});
