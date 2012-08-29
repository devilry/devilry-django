Ext.application({
    name: 'devilry_frontpage',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_frontpage/app',
    paths: {
        'devilry_extjsextras': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras',
        'devilry_header': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_header',
        'devilry_i18n': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_i18n',
        'devilry_authenticateduserinfo': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_authenticateduserinfo',
        'devilry_theme': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_theme'
    },

    requires: [
        'Ext.container.Viewport',
        'Ext.layout.container.Border',
        'Ext.resizer.Splitter',
        'Ext.resizer.SplitterTracker',
        'Ext.resizer.BorderSplitterTracker',

        'Ext.form.field.ComboBox',
        'Ext.form.field.Picker',
        'Ext.form.field.Trigger',
        'Ext.layout.component.field.Trigger',
        'Ext.view.View',
        'Ext.selection.DataViewModel',
        'Ext.selection.Model',
        'Ext.layout.component.BoundList',
        'Ext.toolbar.Paging',
        'Ext.toolbar.TextItem',
        'Ext.form.field.Number',
        'Ext.layout.container.Column',

        'devilry_extjsextras.Router',
        'devilry_extjsextras.RouteNotFound',
        'devilry_header.Header',
        'devilry_header.Breadcrumbs'
    ],

    controllers: [
        'Frontpage'
    ],

    launch: function() {
        this._createViewport();
        this._setupRoutes();
    },

    _createViewport: function() {
        this.breadcrumbs = Ext.widget('breadcrumbs', {
            defaultBreadcrumbs: [{
                text: gettext("Frontpage"),
                url: '#'
            }]
        });

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
                navclass: 'no_role',
                breadcrumbs: this.breadcrumbs
            }, {
                xtype: 'container',
                region: 'center',
                layout: 'border',
                items: [this.primaryContentContainer]
            }]
        });
    },

    setPrimaryContent: function(component) {
        this.primaryContentContainer.removeAll();
        this.primaryContentContainer.add(component);
    },

    /*********************************************
     * Routing
     ********************************************/

    _setupRoutes: function() {
        this.route = Ext.create('devilry_extjsextras.Router', this);
        this.route.add("", 'frontpage');
        this.route.start();
    },
    
    routeNotFound: function(routeInfo) {
        this.breadcrumbs.set([], gettext('Route not found'));
        this.setPrimaryContent({
            xtype: 'routenotfound',
            route: routeInfo.token
        });
    },

    frontpage: function() {
        this.breadcrumbs.setHome();
        this.setPrimaryContent({
            xtype: 'frontpage_overview'
        });
    }
});
