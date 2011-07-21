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
        this.multisearchresultid = this.id + "-multisearchresults";
        Ext.apply(this, {
            items: [{
                xtype: 'multisearchfield'
            }, {
                xtype: 'multisearchresults',
                items: this.searchResultItems,
                id: this.multisearchresultid, // We need to use an id because it may be floating.
                searchWidget: this
            }]
        });

        this.callParent(arguments);
        this.setupSearchEventListeners();
    },

    setupSearchEventListeners: function() {
        var me = this;
        this.getSearchField().addListener('emptyInput', function() {
            me.hideResults();
        });
        this.getSearchField().addListener('newSearchValue', function(value) {
            console.log(value);
            me.search(value);
        });
    },

    getSearchField: function() {
        return this.down('multisearchfield');
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
        return Ext.getCmp(this.multisearchresultid);
    },

    showResults: function() {
        this.getResultContainer().show();
        this.getResultContainer().alignTo(this.getSearchField(), 'bl', [15, 0]);
    },

    hideResults: function() {
        this.getResultContainer().hide();
    },

    search: function(value) {
        var parsedSearch = Ext.create('devilry.extjshelpers.SearchStringParser', {
            searchstring: value
        });
        this.currentParsedSearch = parsedSearch;
        this.showResults();
        Ext.each(this.getResultContainer().items.items, function(searchresults, index, resultgrids) {
            searchresults.search(parsedSearch);
        });
    },

    modifySearch: function(properties) {
        Ext.apply(this.currentParsedSearch, properties);
        this.setSearchValue(this.currentParsedSearch.toString());
    },

    setSearchValue: function(value) {
        this.getSearchField().setValue(value);
    },

    loadInitialValues: function() {
        //var value = 'type:delivery deadline__assignment_group:>:33 3580';
        //var value = 'type:delivery assignment__short_name:week1';
        //var value = 'type:delivery group:'
        //var value = 'type:delivery deadline__assignment_group__parentnode__parentnode__short_name:duck3580';
        //var value = '1100';
        //this.setSearchValue(value);
    }
});
