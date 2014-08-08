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
    requires: [
        'devilry.extjshelpers.searchwidget.SearchResultItem',
        'devilry.extjshelpers.Pager'
    ],
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

        filterconfig: undefined,

        itemtpldata: {
            is_student: undefined
        }
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
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
        var me = this;

        this.showmorebutton = Ext.create('Ext.button.Button', {
            text: 'Show more',
            listeners: {
                click: function() {
                    me.getSearchWidget().modifySearch({
                        type: me.filterconfig.type
                    });
                }
            }
        });

        Ext.apply(this, {
            frame: false,
            hideHeaders: true,
            minButtonWidth: 0,

            tbar: [this.showmorebutton, {
                xtype: 'box',
                flex: 1
            }, {
                xtype: 'devilrypager',
                store: this.store,
                width: 140
            }]
        });
        this.callParent(arguments);

        this.store.addListener('load', function(store, records, successful) {
            if(successful) {
                me.handleStoreLoadSuccess(records);
            } else {
                me.handleStoreLoadFailure();
            }
        });
    },

    getSearchWidget: function() {
        return this.up('multisearchresults').getSearchWidget();
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
        var data = {};
        Ext.apply(data, record.data);
        Ext.apply(data, this.itemtpldata);
        Ext.apply(searchresultitem, {
            xtype: 'searchresultitem',
            recorddata: data,
            recordindex: index,
            itemtpldata: this.itemtpldata
        });
        this.add(searchresultitem);
    },


    search: function(parsedSearch) {
        if(parsedSearch.type && parsedSearch.type != this.filterconfig.type) {
            this.hide();
            return;
        }
        this.store.proxy.extraParams = parsedSearch.applyToExtraParams(this.store.proxy.extraParams, this.filterconfig.shortcuts);
        parsedSearch.applyPageSizeToStore(this.store);
        if(parsedSearch.type) {
            this.enableStandaloneMode();
        } else {
            this.enableSharingMode();
        }
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
    },

    /**
     * @private
     *
     * Used when this SearchResults is the only one beeing displayed.
     */
    enableStandaloneMode: function() {
        this.showmorebutton.hide();
    },

    /**
     * @private
     *
     * Used when this SearchResults is beeing displayed in a box with many other SearchResults.
     */
    enableSharingMode: function() {
        this.showmorebutton.show();
    }
});
