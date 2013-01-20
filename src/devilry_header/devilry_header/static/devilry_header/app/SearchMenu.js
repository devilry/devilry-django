Ext.define('devilry_header.SearchMenu', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader_searchmenu',
    cls: 'devilryheader_searchmenu',
    floating: true,
    frame: false,
    border: 0,
    autoShow: true,
//    autoScroll: true,
    topOffset: 30,

    requires: [
        'devilry_header.store.AdminSearchResults',
        'devilry_header.AdminSearchResultsView'
    ],

    initComponent: function() {
        this._setupAutosizing();
        Ext.apply(this, {
            layout: 'anchor',
            width: 300,
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'textfield',
                emptyText: gettext('Search') + ' ...'
            }, {
                xtype: 'container',
                itemId: 'searchResultsContainer',
                items: [],
                listeners: {
                    scope: this,
                    render: this._onRenderSearchResultsContainer
                }
            }]
        });
        this.callParent(arguments);
    },

    _onRenderSearchResultsContainer:function () {
        this._addSearchResultViews();
    },

    _addSearchResultViews:function () {
        var container = this.down('#searchResultsContainer');
        var store = Ext.create('devilry_header.store.AdminSearchResults');
        store.search({
            search: 'duck'
        }, {
            callback:function (records, op) {
                console.log(records, op);
            }
        });
        this.add({
            xtype: 'devilry_header_adminsearchresults',
            store: store
        });
    },

    _search:function (search) {

    },


    //
    //
    // Autoresize to window size
    //
    //

    _setupAutosizing: function() {
        // Get the DOM disruption over with before the component renders and begins a layout
        Ext.getScrollbarSize();

        // Clear any dimensions, we will size later on
        this.width = this.height = undefined;

        Ext.fly(window).on('resize', this._onWindowResize, this);
        this.on('show', this._onShow, this);
    },

    _onWindowResize: function() {
        if(this.isVisible()) {
            this._setSizeAndPosition();
        }
    },

    _setSizeAndPosition: function() {
        var bodysize = Ext.getBody().getViewSize();
//        this.setSize({
//            width: bodysize.width,
//            height: bodysize.height - this.topOffset
//        });
//        var width = 300;
//        this.setSize({
//            width: width,
//            height: 400
//        });
        var width = this.getSize().width;
        this.setPagePosition(bodysize.width-width-100, this.topOffset);
    },

    _onShow: function() {
        this._setSizeAndPosition();
    }
});
