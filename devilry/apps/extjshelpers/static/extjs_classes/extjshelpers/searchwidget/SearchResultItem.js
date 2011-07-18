/** A search result item (a single row in the search result).
 *
 * @xtype searchresultitem
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchResultItem', {
    extend: 'Ext.container.Container',
    alias: 'widget.searchresultitem',
    config: {
        /**
         * @cfg
         * ``Ext.XTemplate`` formatting template for the text content. _Required_.
         */
        tpl: undefined
    },

    initComponent: function() {
        var template = Ext.create('Ext.XTemplate', this.tpl);
        Ext.apply(this, {
            frame: false,
            items: [{
                xtype: 'component',
                html: template.apply(this.record.data)
            }]
        });
        this.callParent(arguments);
    }
});
