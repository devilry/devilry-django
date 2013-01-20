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
                emptyText: gettext('Search') + ' ...',
                enableKeyEvents: true,
                itemId: 'searchfield',
                listeners: {
                    scope: this,
                    change: this._onSearchFieldChange,
                    keypress: this._onSearchFieldKeyPress
                }
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
        this.add({
            xtype: 'devilry_header_adminsearchresults',
            store: Ext.create('devilry_header.store.AdminSearchResults')
        });
    },


    _onSearchFieldChange:function (field) {
        if(Ext.isEmpty(this.task)) {
            this.task = new Ext.util.DelayedTask(this._search, this, [field]);
        }
        this.task.delay(300);
    },

    _onSearchFieldKeyPress:function (field, e) {
        if(e.getKey() === e.ENTER) {
            if(!Ext.isEmpty(this.task)) {
                this.task.cancel();
            }
            this._search(field);
        }
    },

    _search:function (field) {
        var search = field.getValue();
        this.down('devilry_header_adminsearchresults').search(search);
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
        this.down('#searchfield').focus();
    }
});
