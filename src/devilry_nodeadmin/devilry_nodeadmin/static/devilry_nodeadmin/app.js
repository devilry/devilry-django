Ext.application({
    name: 'devilry_nodeadmin',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_nodeadmin/app',
    paths: {
        'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes',
        'devilry_extjsextras': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras',
        'devilry_theme': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_theme',
        'devilry_i18n': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_i18n',
        'devilry_usersearch': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_usersearch',
        'devilry_header': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_header',
        'devilry_authenticateduserinfo': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_authenticateduserinfo'
    },

    requires: [
        'Ext.container.Viewport',
        'Ext.view.View',
        'Ext.selection.DataViewModel',
        'Ext.selection.Model',

        'devilry_header.Header',
        'devilry_header.Breadcrumbs',

        'devilry_extjsextras.Router',
        'devilry_extjsextras.RouteNotFound',
        'devilry_extjsextras.AlertMessage'
    ],

    controllers: [
        'NodeBrowser',
        'DashboardController'
    ],

    _setupRoutes: function() {
        this.route = Ext.create('devilry_extjsextras.Router', this );
        this.route.add( "", 'showDefault' );
        this.route.add( "/node/", 'showDefault' );
        this.route.add( "/node/:node_id", 'showChildren' );
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
                items: this.primaryContentContainer
            }]
        });
    },


    showDefault: function( routeInfo ) {
        this.setPrimaryContent({
            xtype: 'dashboardoverview'
        });
//        this.setSecondaryContent({
//            html: [ "Denne listen viser kun nodene du administrerer. Klikk på et element for å se ",
//            "de underliggende nivåene, emnene og periodene." ],
//            border: null
//        });
    },

    showChildren: function( routeInfo, node_pk ) {
//        this.setPrimaryContent([
//            {
//                xtype: 'nodeparentlink',
//                node_pk: node_pk
//            },
//            {
//                xtype: 'nodechildrenlist',
//                node_pk: node_pk
//            }
//        ]);
//        this.setSecondaryContent({
//            xtype: 'nodedetailsoverview',
//            node_pk: node_pk
//        })
    },

    //

    setTitle: function(title) {
        window.document.title = Ext.String.format('{0} - Devilry', title);
    }

});
