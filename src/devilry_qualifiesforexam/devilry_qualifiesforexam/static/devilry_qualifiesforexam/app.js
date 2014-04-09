Ext.application({
    name: 'devilry_qualifiesforexam',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_qualifiesforexam/app',
    paths: {
        'devilry_extjsextras': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras',
        'devilry_subjectadmin': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_subjectadmin/app',
        'devilry_theme': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_theme',
        'devilry_i18n': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_i18n',
        'devilry_authenticateduserinfo': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_authenticateduserinfo',
//        'devilry_usersearch': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_usersearch',
        'devilry_header': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_header/app'
    },

    requires: [
        'Ext.container.Viewport',
        'Ext.layout.container.Border',
        'Ext.layout.container.Column',
        'Ext.form.field.ComboBox',
        'Ext.layout.container.Anchor',
        'devilry_extjsextras.Router',
        'devilry_extjsextras.RouteNotFound',
        'devilry_extjsextras.AlertMessage',
        'devilry_header.Header2',
        'devilry_qualifiesforexam.utils.Breadcrumbs',
        'devilry_authenticateduserinfo.UserInfo',
//        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_extjsextras.FloatingAlertmessageList'
    ],

    controllers: [
        'QualifiesForExamSelectPluginController',
        'QualifiesForExamPreviewController',
        'QualifiesForExamShowStatusController',
        'SummaryViewController'
    ],

    refs: [{
        ref: 'alertmessagelist',
        selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
    }, {
        ref: 'header',
        selector: 'viewport devilryheader2'
    }],

    launch: function() {
        this._createViewport();
    },

    _createViewport: function() {
        this.viewport = Ext.create('Ext.container.Viewport', {
            xtype: 'container',
            layout: 'border'
        });
        this.viewport.setLoading();
        devilry_authenticateduserinfo.UserInfo.load(this._onUserInfoLoaded, this);
    },

    _onUserInfoLoaded: function(userInfoRecord) {
        this.userInfoRecord = userInfoRecord;
        this.breadcrumbs = Ext.create('devilry_qualifiesforexam.utils.Breadcrumbs');
        this.primaryContentContainer = Ext.widget('container', {
            region: 'center',
            layout: 'fit'
        });
        this.viewport.removeAll();
        this.viewport.add([{
            xtype: 'devilryheader2',
            region: 'north',
            navclass: 'subjectadmin',
            breadcrumbs: this.breadcrumbs
        }, {
            xtype: 'container',
            region: 'center',
            cls: 'devilry_subtlebg',
            layout: 'fit',
            items: [{
                xtype: 'floatingalertmessagelist',
                itemId: 'appAlertmessagelist',
                anchor: '100%'
            }, this.primaryContentContainer]
        }]);
        this.viewport.setLoading(false);
        this._onViewportReady();
    },

    _onViewportReady: function() {
        this._setupRoutes();
    },

    setPrimaryContent: function(component) {
        this.primaryContentContainer.removeAll();
        this.primaryContentContainer.add(component);
    },

    /** Used by controllers to set the page title (the title-tag). */
    setTitle: function(title) {
        window.document.title = Ext.String.format('{0} - Devilry', title);
    },


    /*********************************************
     * Routing
     ********************************************/

    _setupRoutes: function() {
        this.route = Ext.create('devilry_extjsextras.Router', this);

        // Handle routing request via the querystring.
        // If we get a token in the ``routeto`` attribute, we set the hash to that token,
        // and reload the page with the querystring removed.
        var query = Ext.Object.fromQueryString(window.location.search);
        if(!Ext.isEmpty(query.routeto)) {
            this.route.setHashWithoutEvent(query.routeto);
            window.location.search = '';
        }

        // Setup routes
        this.route.add('/summary/:node_id', 'summary');
        this.route.add('/:periodid/selectplugin', 'selectplugin');
        this.route.add('/:periodid/preview/:pluginid/:pluginsessionid', 'preview');
        this.route.add('/:periodid/showstatus', 'showstatus');
        this.route.start();
    },

    routeNotFound: function(routeInfo) {
        this.breadcrumbs.set([], gettext('Route not found'));
        this.setPrimaryContent({
            xtype: 'routenotfound',
            route: routeInfo.token
        });
    },

    selectplugin: function(routeInfo, periodid) {
        this.getHeader().setNavClass('subjectadmin');
        this.breadcrumbs.setHome();
        this.setPrimaryContent({
            xtype: 'selectplugin',
            periodid: periodid
        });
    },

    preview: function(routeInfo, periodid, pluginid, pluginsessionid) {
        this.getHeader().setNavClass('subjectadmin');
        this.breadcrumbs.setHome();
        this.setPrimaryContent({
            xtype: 'preview',
            periodid: periodid,
            pluginid: pluginid,
            pluginsessionid: pluginsessionid
        });
    },

    showstatus: function(routeInfo, periodid) {
        this.getHeader().setNavClass('subjectadmin');
        this.breadcrumbs.setHome();
        this.setPrimaryContent({
            xtype: 'showstatus',
            periodid: periodid
        });
    },

    summary: function(routeInfo, node_id) {
        this.getHeader().setNavClass('nodeadmin');
        this.breadcrumbs.setHome();
        this.setPrimaryContent({
            xtype: 'summaryview',
            node_id: node_id
        });
    }
});
