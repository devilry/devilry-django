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
        //'ChoosePeriod',
        'assignment.Overview',
        'assignment.EditPublishingTime',
        'managestudents.Overview',
        'managestudents.AddStudentsPlugin'
    ],

    constructor: function() {
        this.addEvents(
           /**
             * @event
             * Fired when an assignment is successfully loaded by the assignment.Overview.
             * @param {subjectadmin.model.Assignment} assignmentRecord
             */
            'assignmentSuccessfullyLoaded',

            /**
             * @event
             * Fired when the students manager on an assigmment is successfully loaded.
             * @param {subjectadmin.controller.managestudents.Overview} manageStudentsController
             */
            'managestudentsSuccessfullyLoaded'
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
        this.route.add("/@@create-new-assignment/:period,:delivery_types", 'createNewAssignment');
        this.route.add("/@@create-new-assignment/@@success", 'createNewAssignmentSuccess');
        //this.route.add("/:subject/:period", 'period_show');
        //this.route.add("/:subject/:period/@@edit", 'period_edit');
        this.route.add("/:subject_shortname/:period_shortname/:assignment_shortname", 'showAssignment');
        this.route.add("/:subject_shortname/:period_shortname/:assignment_shortname/@@manage-students", 'manageStudents');
        this.setupExtraRoutes();
        this.route.start();
    },
    
    /** Primary for TestApplication. However, it may be useful for someone
     * extending this app. */
    setupExtraRoutes: Ext.emptyFn,

    routeNotFound: function(routeInfo) {
        this.breadcrumbs.set([], dtranslate('theme.routenotfound'));
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

    createNewAssignmentChooseperiod: function(routeInfo) {
        this.breadcrumbs.set([], dtranslate('subjectadmin.createnewassignment.title'));
        this.setPrimaryContent({
            xtype: 'chooseperiod'
        });
    },

    createNewAssignment: function(routeInfo, period_id, delivery_types) {
        this.breadcrumbs.set([], dtranslate('subjectadmin.createnewassignment.title'));
        this.setPrimaryContent({
            xtype: 'createnewassignment',
            period_id: period_id,
            delivery_types: delivery_types
        });
    },

    createNewAssignmentSuccess: function(routeInfo) {
        this.breadcrumbs.set([], dtranslate('subjectadmin.createnewassignment.title'));
        this.setPrimaryContent({
            xtype: 'createnewassignment-successpanel'
        });
    },

    showAssignment: function(routeInfo, subject_shortname, period_shortname, assignment_shortname) {
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
            url: routeInfo.url,
            subject_shortname: subject_shortname,
            period_shortname: period_shortname,
            assignment_shortname: assignment_shortname
        });
    },

    manageStudents: function(routeInfo, subject_shortname, period_shortname, assignment_shortname) {
        var subjecturl = '/' + subject_shortname;
        var periodurl = subjecturl + '/' + period_shortname;
        this.breadcrumbs.set([{
            text: subject_shortname,
            url: subjecturl
        }, {
            text: period_shortname,
            url: periodurl
        }, {
            text: assignment_shortname,
            url: periodurl + '/' + assignment_shortname
        }], dtranslate('subjectadmin.managestudents.breadcrumbtitle'));
        this.setPrimaryContent({
            xtype: 'managestudentsoverview',
            subject_shortname: subject_shortname,
            period_shortname: period_shortname,
            assignment_shortname: assignment_shortname
        });
    }
});
