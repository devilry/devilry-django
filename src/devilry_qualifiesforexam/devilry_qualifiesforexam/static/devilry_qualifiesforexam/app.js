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
        'devilry_extjsextras.Router',
        'devilry_extjsextras.RouteNotFound',
        'devilry_extjsextras.AlertMessage',
        'devilry_header.Header',
        'devilry_qualifiesforexam.utils.Breadcrumbs',
//        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_extjsextras.FloatingAlertmessageList'
    ],

    controllers: [
        'QualifiesForExamSelectPluginController',
        'QualifiesForExamPreviewController',
        'QualifiesForExamShowStatusController'
    ],

    refs: [{
        ref: 'alertmessagelist',
        selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
    }],

    launch: function() {
        this._createViewport();
        this._setupRoutes();
    },

    _createViewport: function() {
        this.breadcrumbs = Ext.create('devilry_qualifiesforexam.utils.Breadcrumbs');

        this.primaryContentContainer = Ext.widget('container', {
            region: 'center',
            layout: 'fit'
        });
        this.viewport = Ext.create('Ext.container.Viewport', {
            xtype: 'container',
            layout: 'border',
            items: [{
                xtype: 'devilryheader',
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
            }]
        });
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
        this.route.add('/:periodid/selectplugin', 'selectplugin');
        this.route.add('/:periodid/preview/:pluginsessionid', 'preview');
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
        this.breadcrumbs.setHome();
        this.setPrimaryContent({
            xtype: 'selectplugin',
            periodid: periodid
        });
    },

    preview: function(routeInfo, periodid, pluginsessionid) {
        this.breadcrumbs.setHome();
        this.setPrimaryContent({
            xtype: 'preview',
            periodid: periodid,
            pluginsessionid: pluginsessionid
        });
    },

    showstatus: function(routeInfo, periodid) {
        this.breadcrumbs.setHome();
        this.setPrimaryContent({
            xtype: 'showstatus',
            periodid: periodid
        });
    }
});
