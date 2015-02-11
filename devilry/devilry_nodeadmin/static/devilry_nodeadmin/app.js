var querystring = Ext.Object.fromQueryString(window.location.search);
if(Ext.isEmpty(querystring.routeTo)) {

    Ext.application({
        name: 'devilry_nodeadmin',
        appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_nodeadmin/app',
        paths: {
            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes',
            'devilry_extjsextras': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras',
            'devilry_theme': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_theme',
            'devilry_i18n': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_i18n',
            'devilry_usersearch': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_usersearch',
            'devilry_header': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_header/app',
            'devilry_authenticateduserinfo': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_authenticateduserinfo'
        },

        requires: [
            'Ext.container.Viewport',
            'Ext.view.View',
            'Ext.layout.container.Border',
            'Ext.layout.container.Column',
            'Ext.form.field.ComboBox',
            'Ext.selection.DataViewModel',
            'Ext.selection.Model',
            'Ext.layout.container.Anchor',
            'Ext.util.Cookies',

            'devilry_header.Header2',
            'devilry_header.Breadcrumbs',

            'devilry_extjsextras.Router',
            'devilry_extjsextras.RouteNotFound',
            'devilry_extjsextras.FloatingAlertmessageList'
        ],

        controllers: [
            'NodeBrowserController',
            'DashboardController',
          'AggregatedStudentInfoController'
        ],

        refs: [{
            ref: 'alertmessagelist',
            selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
        }],

        _setupRoutes: function() {
            this.route = Ext.create('devilry_extjsextras.Router', this );
            this.route.add( "", 'showDefault' );
            this.route.add( "/node/", 'showDefault' );
            this.route.add( "/node/:node_id", 'showChildren' );
          this.route.add( "/aggregatedstudentinfo/:user_id", 'showAggregatedStudentInfo' );
            this.route.start();
        },

        launch: function() {
            this._createViewport();
            this._setupRoutes();
        },

        setPrimaryContent: function(component) {
            this.primaryContentContainer.removeAll();
            this.primaryContentContainer.add(component);
        },

        _createViewport: function() {
            this.primaryContentContainer = Ext.widget('container', {
                layout: 'fit'
            });

            this.breadcrumbs = Ext.widget('breadcrumbs');

            this.viewport = Ext.create('Ext.container.Viewport', {
                xtype: 'container',
                layout: 'border',
                split: true,
                items: [{
                    xtype: 'devilryheader2',
                    region: 'north',
                    navclass: 'nodeadmin',
                    breadcrumbs: this.breadcrumbs
                }, {
                    xtype: 'container',
                    region: 'center',
                    layout: 'fit',
                    cls: 'devilry_subtlebg',
                    items: [this.primaryContentContainer, {
                        xtype: 'floatingalertmessagelist', // NOTE: The alertmessagelist available as getAlertMessagelist() - used for errors and information
                        itemId: 'appAlertmessagelist'
                    }]
                }]
            });
        },


        showDefault: function( routeInfo ) {
            this.breadcrumbs.setHome();
            this.setPrimaryContent({
                xtype: 'dashboardoverview'
            });
        },

        showChildren: function( routeInfo, node_pk ) {
            this.setPrimaryContent({
                xtype: 'nodebrowseroverview',
                node_pk: node_pk
            });
        },

        showAggregatedStudentInfo: function(routeInfo, user_id) {
            this.setPrimaryContent({
                xtype: 'aggregatedstudentinfo',
                user_id: user_id
            });
        },

        setTitle: function(title) {
            window.document.title = Ext.String.format('{0} - Devilry', title);
        }
    });
} else {
    /*
    If the user goes to ``/devilry_nodeadmin/?routeTo=/some/path``, we want to
    redirect them to ``/devilry_nodeadmin/#/some/path``. We need this functionality
    because we want to create Django redirect views with a named URL for linking from
    Django templates into devilry_nodeadmin.

    This, along with ``devilry_nodeadmin.utils.UrlLookup`` makes it much easier to
    migrate devilry_nodeadmin pages to regular Django template based views because
    we only have to replace the view with the redirect view, and update UrlLookup,
    instead of updating all the pages linking to the new view.
    */
    var newUrl = Ext.String.format('{0}/devilry_nodeadmin/#{1}',
        window.DevilrySettings.DEVILRY_URLPATH_PREFIX,
        querystring.routeTo);
    window.location = newUrl;
}
