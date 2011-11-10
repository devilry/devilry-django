Ext.define('devilry.statistics.dataview.MinimalGridView', {
    extend: 'devilry.statistics.dataview.BaseView',
    layout: 'fit',

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

    createGrid: function(extraOpts) {
        var gridColumns = this.getGridColumns();
        var gridOpts = Ext.apply({
            multiSelect: true,
            autoScroll: true,
            store: this.loader.store,
            columns: gridColumns
        });
        if(extraOpts) {
            Ext.apply(gridOpts, extraOpts);
        }
        return Ext.widget('grid', gridOpts);
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
