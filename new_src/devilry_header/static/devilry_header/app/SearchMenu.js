Ext.define('devilry_header.SearchMenu', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader_searchmenu',
    cls: 'devilryheader_searchmenu',

    requires: [
        'devilry_authenticateduserinfo.UserInfo',
        'devilry_header.store.StudentSearchResults',
        'devilry_header.StudentSearchResultsView',
        'devilry_header.store.ExaminerSearchResults',
        'devilry_header.ExaminerSearchResultsView',
        'devilry_header.store.AdminSearchResults',
        'devilry_header.AdminSearchResultsView'
    ],

    initComponent: function() {
        this._setupAutosizing();
        Ext.apply(this, {
            layout: 'anchor',
            floating: true,
            frame: false,
            border: 0,
//            autoShow: true,
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
        devilry_authenticateduserinfo.UserInfo.load(function(userInfoRecord) {
            this._addSearchResultViews(userInfoRecord);
        }, this);
    },

    _addSearchResultViews:function (userInfoRecord) {
        var container = this.down('#searchResultsContainer');
        var views = [];

        this.isAdmin = userInfoRecord.isAdmin();
        this.isExaminer = userInfoRecord.get('is_examiner');
        this.isStudent = userInfoRecord.get('is_student');
        var rolecount = 0;
        if(this.isAdmin) {
            rolecount ++;
        }
        if(this.isExaminer) {
            rolecount ++;
        }
        if(this.isStudent) {
            rolecount ++;
        }
        var columnWidth = 1.0 / rolecount;
        var showHeading = rolecount > 1;

        var listeners = {
            scope: this,
            resultLinkClick: this._onResultLinkClick
        };
        if(this.isStudent) {
            views.push({
                xtype: 'devilry_header_studentsearchresults',
                columnWidth: columnWidth,
                showHeading: showHeading,
                store: Ext.create('devilry_header.store.StudentSearchResults'),
                listeners: listeners
            });
        }
        if(this.isExaminer) {
            views.push({
                xtype: 'devilry_header_examinersearchresults',
                columnWidth: columnWidth,
                showHeading: showHeading,
                store: Ext.create('devilry_header.store.ExaminerSearchResults'),
                listeners: listeners
            });
        }
        if(this.isAdmin) {
            views.push({
                xtype: 'devilry_header_adminsearchresults',
                columnWidth: columnWidth,
                showHeading: showHeading,
                store: Ext.create('devilry_header.store.AdminSearchResults'),
                listeners: listeners
            });
        }
        container.add(views);
    },


    _onSearchFieldChange:function (field) {
        if(Ext.isEmpty(this.task)) {
            this.task = new Ext.util.DelayedTask(this._search, this, [field]);
        }
        this.task.delay(500);
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
        if(this.isAdmin) {
            this.down('devilry_header_adminsearchresults').search(search);
        }
        if(this.isExaminer) {
            this.down('devilry_header_examinersearchresults').search(search);
        }
        if(this.isStudent) {
            this.down('devilry_header_studentsearchresults').search(search);
        }
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
        this.setSize({
            width: bodysize.width,
            height: bodysize.height - this.topOffset
        });
        this.setPagePosition(0, this.topOffset);
    },

    _onShow: function() {
        this._setSizeAndPosition();
        Ext.defer(function () {
            this.down('#searchfield').focus();
//            this.down('#searchfield').setValue('Obligatorisk oppgave 1');
        }, 300, this);
    },

    _onResultLinkClick:function () {
        this.hide();
    }
});
