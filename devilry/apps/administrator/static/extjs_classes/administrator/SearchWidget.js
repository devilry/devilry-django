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

    getSearchField: function() {
        return this.items.items[0];
    },

    focusOnSearchfield: function() {
        this.getSearchField().focus();
    },

    /**
     * @private
     *
     * Get the result container, which we expect to be the second item in this
     * container. */
    getResultContainer: function() {
        //return this.items.items[1];
        return Ext.getCmp('floating-searchresult');
    },

    showResults: function() {
        this.getResultContainer().show();
        this.getResultContainer().alignTo(this.getSearchField());
    },

    hideResults: function() {
        this.getResultContainer().hide();
    },

    search: function(value) {
        this.showResults();
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
        //this.search("");
    }
});
