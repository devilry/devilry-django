Ext.define('devilry.statistics.dataview.MinimalGridView', {
    extend: 'devilry.statistics.dataview.BaseView',

    labelTpl: Ext.create('Ext.XTemplate',
        '<ul class="labels-list">',
        '    <tpl for="labels">',
        '       <li class="label-{.}">{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    _getGridColumns: function() {
        var me = this;
        var gridColumns = [{
            header: 'Username', dataIndex: 'username'
        }, {
            header: 'Labels', dataIndex: 'labels',
            width: 150,
            renderer: function(value, p, record) {
                return me.labelTpl.apply(record.data);
            }
        }];
        return gridColumns;
    },

    refresh: function() {
        var gridColumns = this._getGridColumns();
        var store = this.loader._createStore();
        this.removeAll();
        this.add({
            xtype: 'grid',
            autoScroll: true,
            store: store,
            columns: gridColumns
        });
    }
});
