/** A panel containing multiple search results under a common title and store.
 *
 *      ------------------------
 *      | title                |
 *      ------------------------
 *      | result 1             |
 *      | result 2             |
 *      | result 3             |
 *      -----------------------|
 *
 * @xtype searchresults
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchResults', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.searchresults',
    requires: ['devilry.extjshelpers.searchwidget.SearchResultItem'],
    cls: 'searchresults',
    config: {
        /**
         * @cfg
         * Editor url prefix (__Required__). The editor url for a specific
         * item is ``editorurlprefix+id``. Note that this means that editorurlprefix _must_
         * end with ``/``. _Required_.
         */
        editorurlprefix: undefined,

        /**
         * @cfg
         * Title of these search results. _Required_.
         */
        title: undefined,

        /**
         * @cfg
         * The ``Ext.data.store`` where the results are loaded from. _Required_.
         */
        store: undefined,

        /**
         * @cfg
         * Formatting template for the text rendered for each result item. _Required_.
         */
        rowformattpl: undefined
    },

    initComponent: function() {
        Ext.apply(this, {
            frame: false,
            hideHeaders: true
        });
        this.callParent(arguments);

        var me = this;
        this.store.addListener('load', function(store, records, successful) {
            if(successful) {
                me.handleStoreLoadSuccess(records);
            } else {
                me.handleStoreLoadFailure();
            }
        });
    },

    handleStoreLoadFailure: function() {
        console.log('Failed to load store'); // TODO Better error handling
    },

    handleStoreLoadSuccess: function(records) {
        var me = this;
        Ext.each(records, function(record, index) {
            me.addRecord(record, index);
        });
    },

    addRecord: function(record, index) {
        var searchresultitem = Ext.clone(this.resultitemConfig);
        Ext.apply(searchresultitem, {
            xtype: 'searchresultitem',
            recorddata: record.data,
            even: index%2 != 0
        });
        this.add(searchresultitem);
    }
});
