Ext.define('devilry.statistics.dataview.MinimalGridView', {
    extend: 'devilry.statistics.dataview.BaseView',

    labelTpl: Ext.create('Ext.XTemplate',
        '<ul class="labels-list">',
        '    <tpl for="labelKeys">',
        '       <li class="label-{.}">{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    _getGridColumns: function() {
        var me = this;
        var gridColumns = [{
            header: 'Username', dataIndex: 'username'
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
        var gridColumns = this._getGridColumns();
        this.removeAll();
        this.grid = this.add({
            xtype: 'grid',
            multiSelect: true,
            autoScroll: true,
            store: this.loader.store,
            columns: gridColumns
        });
    },

    getSelectedStudents: function() {
        return this.grid.getSelectionModel().getSelection();
    }
});
