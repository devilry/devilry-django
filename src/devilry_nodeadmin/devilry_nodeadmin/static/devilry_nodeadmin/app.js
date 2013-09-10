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

        'devilry_header.Header',
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
      this.route.add( "/aggstud/", 'showAggregatedStudentInfo' );
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
                xtype: 'devilryheader',
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

  showAggregatedStudentInfo: function(routeInfo) {
            this.setPrimaryContent({
            xtype: 'aggregatedstudentinfo'
        });
  }

    //

    setTitle: function(title) {
        window.document.title = Ext.String.format('{0} - Devilry', title);
    }

});
