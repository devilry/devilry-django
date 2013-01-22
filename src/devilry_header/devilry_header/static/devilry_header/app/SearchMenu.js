Ext.define('devilry_header.SearchMenu', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader_searchmenu',
    cls: 'devilryheader_searchmenu',

    requires: [
        'devilry_header.store.AdminSearchResults',
        'devilry_header.AdminSearchResultsView',
        'devilry_header.store.ExaminerSearchResults',
        'devilry_header.ExaminerSearchResultsView'
    ],

    initComponent: function() {
        this._setupAutosizing();
        Ext.apply(this, {
            layout: 'anchor',
            floating: true,
            frame: false,
            border: 0,
            autoShow: true,
            autoScroll: true,
            topOffset: 30,
            padding: 20,
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'textfield',
                emptyText: gettext('Search') + ' ...',
                enableKeyEvents: true,
                itemId: 'searchfield',
                cls: 'searchmenu_searchfield',
                listeners: {
                    scope: this,
                    change: this._onSearchFieldChange,
                    keypress: this._onSearchFieldKeyPress
                }
            }, {
                xtype: 'container',
                itemId: 'searchResultsContainer',
                layout: 'column',
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
        var views = [];
        views.push({
            xtype: 'devilry_header_adminsearchresults',
            columnWidth: 0.5,
            store: Ext.create('devilry_header.store.AdminSearchResults')
        });
        views.push({
            xtype: 'devilry_header_examinersearchresults',
            columnWidth: 0.5,
            store: Ext.create('devilry_header.store.ExaminerSearchResults')
        });
        container.add(views);
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
        this.down('devilry_header_examinersearchresults').search(search);
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
//        var bodysize = Ext.getBody().getViewSize();
//        var size = this.getSize();
//        this.setPagePosition(bodysize.width - size.width - 100, this.topOffset);
        var bodysize = Ext.getBody().getViewSize();
        this.setSize({
            width: bodysize.width,
            height: bodysize.height - this.topOffset
        });
        this.setPagePosition(0, this.topOffset);
    },

    _onShow: function() {
        this._setSizeAndPosition();
        this.down('#searchfield').focus();
        Ext.defer(function () {
            this.down('#searchfield').setValue('donald');
        }, 300, this);
    }
});
