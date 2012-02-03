/** Subjectadmin Application. */
Ext.define('subjectadmin.Application', {
    extend: 'Ext.app.Application',

    name: 'subjectadmin',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/subjectadmin/app',

    requires: [
        'Ext.container.Viewport',
        'jsapp.Router',
        'themebase.RouteNotFound',
        'themebase.Breadcrumbs'
    ],

    controllers: [
        'Shortcuts',
        'Dashboard',
        'CreateNewAssignment',
        'ChoosePeriod',
        'assignment.Overview',
        'assignment.EditPublishingTime'
    ],

    constructor: function() {
        this.addEvents(
           /**
             * @event
             * Fired when an assignment is successfully loaded by the assignment.Overview.
             * @param {subjectadmin.model.Assignment} assignmentRecord
             */
            'assignmentSuccessfullyLoaded'
        );
        this.callParent(arguments);
    },

    launch: function() {
        this._createViewport();
        this._setupRoutes();
    },

    _createViewport: function() {
        this.breadcrumbs = Ext.widget('breadcrumbs', {
            region: 'north',
            //height: 30
        });
        this.primaryContentContainer = Ext.widget('container', {
            region: 'center',
            layout: 'fit'
        });
        this.viewport = Ext.create('Ext.container.Viewport', {
            layout: 'border',
            items: [this.breadcrumbs, this.primaryContentContainer]
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
        this.route = Ext.create('jsapp.Router', this);
        this.route.add("", 'dashboard');
        this.route.add("/@@create-new-assignment/@@chooseperiod", 'createNewAssignmentChooseperiod');
        this.route.add("/@@create-new-assignment/:period", 'createNewAssignment');
        //this.route.add("/:subject/:period", 'period_show');
        //this.route.add("/:subject/:period/@@edit", 'period_edit');
        this.route.add("/:subject_shortname/:period_shortname/:assignment_shortname", 'assignmentShow');
        this.setupExtraRoutes();
        this.route.start();
    },
    
    /** Primary for TestApplication. However, it may be useful for someone
     * extending this app. */
    setupExtraRoutes: Ext.emptyFn,

    routeNotFound: function(route) {
        this.breadcrumbs.set([], dtranslate('theme.routenotfound'));
        this.breadcrumbs.set([], dtranslate('subjectadmin.chooseperiod.title'));
        this.setPrimaryContent({
            xtype: 'routenotfound',
            route: route.token
        });
    },

    dashboard: function() {
        this.breadcrumbs.setHome();
        this.setPrimaryContent({
            xtype: 'dashboard'
        });
    },

    createNewAssignmentChooseperiod: function(info) {
        this.breadcrumbs.set([], dtranslate('subjectadmin.chooseperiod.title'));
        this.setPrimaryContent({
            xtype: 'chooseperiod',
            nexturlformat: '/@@create-new-assignment/{0}'
        });
    },

    createNewAssignment: function(info, periodId) {
        this.breadcrumbs.set([], dtranslate('subjectadmin.createnewassignment.title'));
        this.setPrimaryContent({
            xtype: 'createnewassignment',
            periodId: periodId
        });
    },

    assignmentShow: function(info, subject_shortname, period_shortname, assignment_shortname) {
        var subjecturl = '/' + subject_shortname;
        this.breadcrumbs.set([{
            text: subject_shortname,
            url: subjecturl
        }, {
            text: period_shortname,
            url: subjecturl + '/' + period_shortname
        }], assignment_shortname);
        this.setPrimaryContent({
            xtype: 'assignmentoverview',
            subject_shortname: subject_shortname,
            period_shortname: period_shortname,
            assignment_shortname: assignment_shortname
        });
    }
});
