/**
 * Search widget with a {@link devilry.administrator.MultiSearchField} on top
 * and results in a {@link devilry.administrator.MultiSearchResults} below.
 *
 *     Search: ______________
 *    
 *     |Result1             |
 *     +--------------------|
 *     |                    |
 *     |                    |
 *     |                    |
 *     +--------------------+
 *    
 *     |Result2             |
 *     +--------------------|
 *     |                    |
 *     |                    |
 *     |                    |
 *     +--------------------+
 *
 * @xtype administratorsearchwidget
 * @cfg {[Object]} searchResultItems Item list forwarded to the item config of {@link devilry.administrator.MultiSearchResults}
 * */
Ext.define('devilry.administrator.SearchWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.administratorsearchwidget',
    requires: [
        'devilry.administrator.SearchResults',
        'devilry.administrator.MultiSearchField',
        'devilry.administrator.MultiSearchResults'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'administratormultisearchfield'
            }, {
                xtype: 'administratormultisearchresults',
                items: this.searchResultItems
            }]
        });

        this.callParent(arguments);
    },

    focusOnSearchfield: function() {
        var searchfield = this.items.items[0];
        searchfield.focus();
    },

    /**
     * @private
     *
     * Get the result container, which we expect to be the second item in this
     * container. */
    getResultContainer: function() {
        return this.items.items[1];
    },

    search: function(value) {
        Ext.each(this.getResultContainer().items.items, function(searchresults, index, resultgrids) {
            var store = searchresults.store;
            store.proxy.extraParams.query = value;
            store.load(function(records, operation, success) {
                if(store.data.items.length == 0) {
                    searchresults.hide();
                } else {
                    searchresults.show();
                }
            });
        });
    },

    loadInitialValues: function() {
        this.search("");
    }
});
