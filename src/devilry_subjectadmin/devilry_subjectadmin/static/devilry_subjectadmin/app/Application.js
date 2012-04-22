/** Subjectadmin Application. */
Ext.define('devilry_subjectadmin.Application', {
    extend: 'Ext.app.Application',

    name: 'devilry_subjectadmin',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_subjectadmin/app',

    requires: [
        'Ext.container.Viewport',
        'jsapp.Router',
        'themebase.RouteNotFound',
        'themebase.AlertMessage',
        'themebase.DevilryHeader',
        'themebase.Breadcrumbs'
    ],

    controllers: [
        'Shortcuts',
        'Dashboard',
        'CreateNewAssignment',
        'subject.ListAll',
        'subject.Overview',
        'period.Overview',
        'assignment.Overview',
        'assignment.EditPublishingTime',
        'assignment.EditAnonymous',
        'managestudents.Overview',
        'managestudents.AddStudentsPlugin',
        'managestudents.NoGroupSelectedViewPlugin',
        'managestudents.SingleGroupSelectedViewPlugin',
        'managestudents.MultipleGroupsSelectedViewPlugin'
    ],

    constructor: function() {
        this.addEvents(
           /**
             * @event
             * Fired when an assignment is successfully loaded by the assignment.Overview.
             * @param {devilry_subjectadmin.model.Assignment} assignmentRecord
             */
            'assignmentSuccessfullyLoaded',

            /**
             * @event
             * Fired when the students manager on an assigmment is successfully loaded.
             * @param {devilry_subjectadmin.controller.managestudents.Overview} manageStudentsController
             */
            'managestudentsSuccessfullyLoaded',

            /**
             * @event
             * Fired when no groups are selected in the students manager on an
             * assignment. This happens when the manager is loaded, and
             * whenever all groups are deselected.
             * @param {devilry_subjectadmin.controller.managestudents.Overview} manageStudentsController
             */
            'managestudentsNoGroupSelected',

            /**
             * @event
             * Fired when a single group is selected in the students manager on
             * an assignment.
             * @param {devilry_subjectadmin.controller.managestudents.Overview} manageStudentsController
             * @param {devilry_subjectadmin.model.Group} groupRecord
             */
            'managestudentsSingleGroupSelected',

            /**
             * @event
             * Fired when multiple groups are selected in the students manager
             * on an assignment.
             * @param {devilry_subjectadmin.controller.managestudents.Overview} manageStudentsController
             * @param {[devilry_subjectadmin.model.Group]} groupRecords
             */
            'managestudentsMultipleGroupsSelected'
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
            xtype: 'container',
            layout: 'border',
            items: [{
                xtype: 'devilryheader',
                region: 'north',
                navclass: 'subjectadmin'
            }, {
                xtype: 'container',
                region: 'center',
                layout: 'border',
                items: [this.breadcrumbs, this.primaryContentContainer]
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
        this.route = Ext.create('jsapp.Router', this);
        this.route.add("", 'dashboard');
        this.route.add("/", 'browse');
        this.route.add("/:subject_shortname/", 'showSubject');
        this.route.add("/:subject_shortname/:period_shortname/", 'showPeriod');
        this.route.add("/@@create-new-assignment/@@success", 'createNewAssignmentSuccess');
        this.route.add("/@@create-new-assignment/:period", 'createNewAssignment'); // Must come after @@success (if not, it will match @@success)
        //this.route.add("/:subject/:period", 'period_show');
        //this.route.add("/:subject/:period/@@edit", 'period_edit');
        this.route.add("/:subject_shortname/:period_shortname/:assignment_shortname/", 'showAssignment');
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

    browse: function(routeInfo) {
        this.breadcrumbs.set([], dtranslate('devilry_subjectadmin.allsubjects'));
        this.setPrimaryContent({
            xtype: 'subjectlistall'
        });
    },

    showSubject: function(routeInfo, subject_shortname) {
        var subjecturl = '/' + subject_shortname;
        this.breadcrumbs.set([{
            text: dtranslate('devilry_subjectadmin.allsubjects'),
            url: '/'
        }], subject_shortname);
        this.setPrimaryContent({
            xtype: 'subjectoverview',
            subject_shortname: subject_shortname
        });
    },

    showPeriod: function(routeInfo, subject_shortname, period_shortname) {
        var subjecturl = '/' + subject_shortname + '/';
        this.breadcrumbs.set([{
            text: dtranslate('devilry_subjectadmin.allsubjects'),
            url: '/'
        }, {
            text: subject_shortname,
            url: subjecturl
        }], period_shortname);
        this.setPrimaryContent({
            xtype: 'periodoverview',
            subject_shortname: subject_shortname,
            period_shortname: period_shortname
        });
    },

    createNewAssignment: function(routeInfo, period_id) {
        this.breadcrumbs.set([], dtranslate('devilry_subjectadmin.createnewassignment.title'));
        this.setPrimaryContent({
            xtype: 'createnewassignment',
            period_id: period_id
        });
    },

    createNewAssignmentSuccess: function(routeInfo) {
        this.breadcrumbs.set([], dtranslate('devilry_subjectadmin.createnewassignment.title'));
        this.setPrimaryContent({
            xtype: 'createnewassignment-successpanel'
        });
    },

    showAssignment: function(routeInfo, subject_shortname, period_shortname, assignment_shortname) {
        var subjecturl = '/' + subject_shortname + '/';
        this.breadcrumbs.set([{
            text: dtranslate('devilry_subjectadmin.allsubjects'),
            url: '/'
        }, {
            text: subject_shortname,
            url: subjecturl
        }, {
            text: period_shortname,
            url: subjecturl + period_shortname + '/'
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
        var subjecturl = '/' + subject_shortname + '/';
        var periodurl = subjecturl + period_shortname + '/';
        this.breadcrumbs.set([{
            text: dtranslate('devilry_subjectadmin.allsubjects'),
            url: '/'
        }, {
            text: subject_shortname,
            url: subjecturl
        }, {
            text: period_shortname,
            url: periodurl
        }, {
            text: assignment_shortname,
            url: periodurl + assignment_shortname + '/'
        }], dtranslate('devilry_subjectadmin.managestudents.breadcrumbtitle'));
        this.setPrimaryContent({
            xtype: 'managestudentsoverview',
            subject_shortname: subject_shortname,
            period_shortname: period_shortname,
            assignment_shortname: assignment_shortname
        });
    }
});
