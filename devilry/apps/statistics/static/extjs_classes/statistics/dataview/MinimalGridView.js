Ext.define('devilry.statistics.dataview.MinimalGridView', {
    extend: 'devilry.statistics.dataview.BaseView',

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
            header: 'Full name', dataIndex: 'full_name',
            minWidth: 140,
            flex: 2,
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

    refreshView: function() {
        var gridColumns = this.getGridColumns();
        this.removeAll();
        this.grid = this.add({
            xtype: 'grid',
            multiSelect: true,
            autoScroll: true,
            store: this.loader.store,
            columns: gridColumns,
            listeners: {
                scope: this,
                select: function(grid, record) {
                    this.up('statistics-dataview').fireEvent('selectStudent', record);
                }
            }
        });
    },

    getSelectedStudents: function() {
        return this.grid.getSelectionModel().getSelection();
    }
});
