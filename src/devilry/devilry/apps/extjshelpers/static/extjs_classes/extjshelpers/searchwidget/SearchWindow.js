Ext.define('devilry.extjshelpers.searchwidget.SearchWindow', {
    extend: 'Ext.window.Window',
    closeAction: 'hide',
    plain: true,
    maximizable: false,
    maximized: true,
    modal: true,

    requires: [
        'devilry.extjshelpers.SearchField',
        'devilry.extjshelpers.searchwidget.MultiSearchResults'
    ],

    /**
     * @cfg {Object} [searchWidget]
     */

    /**
     * @cfg {Object} [searchResultItems]
     */

    /**
     * @cfg {string} [emptyText]
     * Empty text of the search field.
     */
    emptyText: gettext('Search for anything...'),

    initComponent: function() {
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'searchfield',
                margin: 5,
                emptyText: this.emptyText
            }, {
                xtype: 'multisearchresults',
                items: this.searchResultItems,
                searchWidget: this,
                flex: 1
            }],

            listeners: {
                scope: this,
                show: this._forceFocus,
                render: this._forceFocus
            }
        });
        this.callParent(arguments);
        this.setupSearchEventListeners();
    },

    _forceFocus: function() {
        Ext.defer(function() {
            this.getSearchField().focus();
        }, 200, this);
    },

    setupSearchEventListeners: function() {
        var me = this;
        this.getSearchField().addListener('emptyInput', function() {
            me.search('');
        });
        this.getSearchField().addListener('newSearchValue', function(value) {
            //console.log(value);
            me.search(value);
        });
    },

    /**
     * @private
     */
    getSearchField: function() {
        return this.down('searchfield');
    },

    /**
     * @private
     */
    getResultContainer: function() {
        return this.down('multisearchresults');
    },

    search: function(value) {
        Ext.each(this.getResultContainer().items.items, function(searchresults, index, resultgrids) {
            var parsedSearch = Ext.create('devilry.extjshelpers.SearchStringParser', {
                searchstring: value,
                alwaysAppliedFilters: searchresults.alwaysAppliedFilters
            });
            searchresults.search(parsedSearch);
        });

        // Create a parsed search without any alwaysAppliedFilters for modifySearch() to use
        var parsedSearch = Ext.create('devilry.extjshelpers.SearchStringParser', {
            searchstring: value
        });
        this.currentParsedSearch = parsedSearch;
    },

    modifySearch: function(properties) {
        Ext.apply(this.currentParsedSearch, properties);
        this.setSearchValue(this.currentParsedSearch.toString());
    },

    setSearchValue: function(value) {
        this.getSearchField().setValue(value);
    }
});
