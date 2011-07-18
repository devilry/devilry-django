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
    hidden: true,
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
        rowformattpl: undefined,

        filterconfig: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        var filterconfig = {
            type: undefined,
            shortcuts: new Object()
        };
        if(this.filterconfig) {
            Ext.apply(filterconfig, this.filterconfig);
        }
        this.filterconfig = filterconfig;
        return this;
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
        //console.log('Failed to load store'); // TODO Better error handling
    },

    handleStoreLoadSuccess: function(records) {
        this.removeAll();
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
            recordindex: index
        });
        this.add(searchresultitem);
    },


    search: function(parsedSearch) {
        if(parsedSearch.type && parsedSearch.type != this.filterconfig.type) {
            return;
        }
        this.store.proxy.extraParams = parsedSearch.applyToExtraParams(this.store.proxy.extraParams, this.filterconfig.shortcuts);
        console.log(this.store.proxy.extraParams);
        this.loadStore();
    },

    loadStore: function() {
        var me = this;
        this.store.load(function(records, operation, success) {
            if(success) {
                if(me.store.data.items.length == 0) {
                    me.hide();
                } else {
                    me.show();
                }
            } else {
                me.hide();
            }
        });
    }
});
