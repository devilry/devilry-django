/** A grid containing search results.
 *
 * @xtype administratorsearchresults
 * */
Ext.define('devilry.administrator.SearchResults', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.administratorsearchresults',
    config: {
        /**
         * @cfg
         * Editor url prefix (__Required__). The editor url for a specific
         * item is ``editorurlprefix+id``. Note that this means that editorurlprefix _must_
         * end with ``/``.
         */
        editorurlprefix: ''
    },

    initComponent: function() {
        Ext.apply(this, {
            width: 600,
            margin: {bottom: 20},
            //height: 150,
            frame: false,
            //title: false,
            hideHeaders: true,
            columns: [{
                header: 'Nodes', dataIndex: 'long_name', flex: 1,
                renderer: this.formatRowWrapper
            }]
        });
        this.callParent(arguments);
    },

    formatRowWrapper: function(value, p, record) {
        return this.formatRow(record);
    },

    formatRow: function(record) {
        return this.getFormattedRow(
            record.get('long_name'),
            record.get('short_name'));
    },

    getFormattedRow: function(title, subtitle) {
        return Ext.String.format(
            '<div class="important">{0}</div><div class="unimportant">{1}</div>',
            title, subtitle);
    },

    listeners: {
        selectionchange: function(view, selections, options) {
            var record = selections[0].data;
            window.location = Ext.String.format('{0}{1}',  this.editorurlprefix, record.id);
        }
    },

    deselectAll: function() {
        Ext.each(this.ownerCt.items.items, function(grid, index, resultgrids) {
            grid.getSelectionModel().deselectAll();
        });
    }
});
