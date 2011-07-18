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
        'devilry.extjshelpers.searchwidget.MultiSearchResults',
        'devilry.extjshelpers.SearchStringParser'
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

    //hideResults: function() {
        //this.getResultContainer().hide();
    //},

    search: function(value) {
        var parsedSearch = Ext.create('devilry.extjshelpers.SearchStringParser', {
            searchstring: value
        });
        this.showResults();
        Ext.each(this.getResultContainer().items.items, function(searchresults, index, resultgrids) {
            searchresults.search(parsedSearch);
        });
    },

    loadInitialValues: function() {
        //var value = 'type:delivery deadline__assignment_group:>:33 3580';
        var value = 'type:delivery assignment__short_name:week1';
        //var value = 'type:delivery deadline__assignment_group__parentnode__parentnode__short_name:duck3580';
        //var value = '3580';
        this.getSearchField().setValue(value);
        //this.search(value);
    }
});
