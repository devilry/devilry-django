/**
 * Search widget with a {@link devilry.extjshelpers.searchwidget.MultiSearchField} on top
 * and results in a {@link devilry.extjshelpers.searchwidget.MultiSearchResults} below.
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
 * @xtype searchwidget
 * @cfg {[Object]} searchResultItems Item list forwarded to the item config of {@link devilry.extjshelpers.searchwidget.MultiSearchResults}
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.searchwidget',
    requires: [
        'devilry.extjshelpers.searchwidget.SearchResults',
        'devilry.extjshelpers.searchwidget.MultiSearchField',
        'devilry.extjshelpers.searchwidget.MultiSearchResults'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'multisearchfield'
            }, {
                xtype: 'multisearchresults',
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
        this.getResultContainer().alignTo(this.getSearchField(), 'bl', [15, 0]);
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
        //this.search("3580");
    }
});
