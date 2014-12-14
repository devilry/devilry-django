/*

## Events

``new_mathjax_math``
    Fired each time mathjax has completed loading math.

*/
Ext.application({
    name: 'devilry_student',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_student/app',
    paths: {
        'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes',
        'devilry_extjsextras': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras',
        'devilry_header': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_header/app',
        'devilry_authenticateduserinfo': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_authenticateduserinfo',
        'devilry_i18n': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_i18n',
        'devilry_theme': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_theme'
    },

    requires: [
        'Ext.container.Viewport',
        'Ext.layout.container.Border',
        'Ext.layout.container.Column',
        'Ext.form.Panel',
        'Ext.form.Basic',
        'Ext.form.action.Load',
        'Ext.form.action.Action',
        'Ext.form.action.Submit',
        'Ext.form.field.Hidden',
        'Ext.resizer.BorderSplitter',
        'Ext.resizer.Splitter',
        'Ext.resizer.SplitterTracker',
        'devilry_extjsextras.Router',
        'devilry_extjsextras.RouteNotFound',
        'devilry_header.Header2',
        'devilry_header.Breadcrumbs'
    ],

    controllers: [
        'Dashboard',
        'GroupInfo',
        'AddDelivery',
        'BrowseGroupedController'
    ],

    launch: function() {
        this.dashboard_url = DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_student/';
        this._createViewport();
        this._setupRoutes();
        if(window.DevilrySettings.DEVILRY_ENABLE_MATHJAX) {
            MathJax.Hub.Register.MessageHook("New Math", Ext.bind(this._onNewMathJaxMath, this));
        }
    },

    _onNewMathJaxMath: function(message) {
        this.fireEvent('new_mathjax_math', message);
    },

    _createViewport: function() {
        this.breadcrumbs = Ext.widget('breadcrumbs');

        this.primaryContentContainer = Ext.widget('container', {
            layout: 'fit'
        });
        this.viewport = Ext.create('Ext.container.Viewport', {
            xtype: 'container',
            layout: 'border',
            items: [{
                xtype: 'devilryheader2',
                region: 'north',
                navclass: 'student',
                breadcrumbs: this.breadcrumbs
            }, {
                xtype: 'container',
                region: 'center',
                layout: 'fit',
                cls: 'devilry_subtlebg',
                items: [this.primaryContentContainer]
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
        this.route.add("", 'dashboard');
        this.route.add("/browsegrouped/active", 'browsegrouped_active');
        this.route.add("/browsegrouped/history", 'browsegrouped_history');
        this.route.add("/group/:group_id/", 'groupinfo');
        this.route.add("/group/:group_id/@@add-delivery", 'groupinfoAddDelivery');
        this.route.add("/group/:group_id/:delivery_id", 'groupinfo');
        this.route.start();
    },
    
    routeNotFound: function(routeInfo) {
        this.breadcrumbs.set([], gettext('Route not found'));
        this.setPrimaryContent({
            xtype: 'routenotfound',
            route: routeInfo.token
        });
    },

    dashboard: function() {
        this.breadcrumbs.setHome();
        this.setPrimaryContent({
            xtype: 'dashboard'
        });
    },

    browsegrouped_history: function() {
        this.setPrimaryContent({
            xtype: 'browsegrouped',
            activeonly: false
        });
    },

    browsegrouped_active: function() {
        this.setPrimaryContent({
            xtype: 'browsegrouped',
            activeonly: true
        });
    },

    groupinfo: function(routeinfo, group_id, delivery_id, add_delivery) {
        this.setPrimaryContent({
            xtype: 'groupinfo',
            group_id: group_id,
            delivery_id: delivery_id,
            add_delivery: add_delivery
        });
    },

    groupinfoAddDelivery: function(routeinfo, group_id) {
        this.groupinfo(routeinfo, group_id, undefined, true);
    }
});
