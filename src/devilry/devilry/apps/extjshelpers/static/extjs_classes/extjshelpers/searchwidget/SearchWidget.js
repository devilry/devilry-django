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
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.searchwidget',
    cls: 'widget-searchwidget',
    requires: [
        'devilry.extjshelpers.SearchField',
        'devilry.extjshelpers.searchwidget.SearchResults',
        'devilry.extjshelpers.searchwidget.MultiSearchResults',
        'devilry.extjshelpers.SearchStringParser',
        'devilry.extjshelpers.searchwidget.SearchWindow'
    ],

    config: {
        /**
         * @cfg
         * The {@link devilry.extjshelpers.searchwidget.SearchResults}, use
         * when searching.
         */
        searchResultItems: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.searchwindow = Ext.create('devilry.extjshelpers.searchwidget.SearchWindow', {
            searchResultItems: this.searchResultItems,
            searchWidget: this
        });
        this.searchwindow.on('hide', function() {
            this.getSearchField().setValue('');
        }, this);
        this.searchfield = Ext.widget('searchfield', {
            emptyText: 'Search for anything...',
            flex: 1
        });

        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            height: 50,
            items: [this.searchfield, {
                xtype: 'button',
                text: 'Browse',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: function() {
                        this.search('');
                    }
                }
            }]
        });

        this.callParent(arguments);
        this.setupSearchEventListeners();
    },

    setupSearchEventListeners: function() {
        var me = this;
        this.getSearchField().addListener('newSearchValue', function(value) {
            me.search(value);
        });
    },

    getSearchField: function() {
        return this.searchfield;
    },

    focusOnSearchfield: function() {
        this.getSearchField().focus();
    },

    search: function(value) {
        this.searchwindow.show();
        this.searchwindow.setSearchValue(value);
        this.searchwindow.getSearchField().triggerSearch(value);
    },

    loadInitialValues: function() {
        //var value = 'type:delivery deadline__assignment_group:>:33 3580';
        //var value = 'type:delivery assignment__short_name:week1';
        //var value = 'type:delivery group:'
        //var value = 'type:delivery deadline__assignment_group__parentnode__parentnode__short_name:duck3580';
        //var value = '';
        //this.search(value);
    }
});
