Ext.application({
    name: 'devilry_subjectadmin',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_subjectadmin/app',
    paths: {
        'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes',
        'devilry_extjsextras': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras',
        'devilry_theme': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_theme',
        'devilry_usersearch': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_usersearch'
    },

    requires: [
        'Ext.container.Viewport',
        'devilry_extjsextras.Router',
        'devilry_extjsextras.RouteNotFound',
        'devilry_extjsextras.AlertMessage',
        'devilry_extjsextras.DevilryHeader',
        'devilry_extjsextras.Breadcrumbs'
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
        'managestudents.Select',
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
            'managestudentsMultipleGroupsSelected',

            /**
             * @event
             * Fired when the sorter for the Groups list is changed.
             * @param {String} [sorter]
             */
            'managestudentsGroupSorterChanged'
        );
        this.callParent(arguments);
    },

    launch: function() {
        this._createViewport();
        this._setupRoutes();
    },

    _createViewport: function() {
        this.breadcrumbs = Ext.widget('breadcrumbs', {
            region: 'north'
            //defaultBreadcrumbs: [{
                //text: gettext("Subjectadmin"),
                //url: ''
            //}]
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

    /** Called after something has been deleted.
     * @param short_description A short description of the item that was deleted.
     * */
    onAfterDelete: function(short_description) {
        this.route.navigate('');
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
        this.route.add("/", 'browse');
        this.route.add("/subject/:subject_id/", 'showSubject');
        this.route.add("/period/:period_id/", 'showPeriod');
        this.route.add("/assignment/:assignment_id/", 'showAssignment');
        this.route.add("/assignment/:assignment_id/@@manage-students/", 'manageStudents');
        this.route.add("/assignment/:assignment_id/@@manage-students/@@select/:group_ids", 'manageGroupsSelectGroups');
        this.route.add("/assignment/:assignment_id/@@manage-students/@@add-students", 'manageGroupsAddStudents');
        this.route.add("/@@create-new-assignment/@@success", 'createNewAssignmentSuccess');
        this.route.add("/@@create-new-assignment/:period", 'createNewAssignment'); // Must come after @@success (if not, it will match @@success)
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

    browse: function(routeInfo) {
        this.breadcrumbs.set([], gettext("All subjects"));
        this.setPrimaryContent({
            xtype: 'subjectlistall'
        });
    },

    showSubject: function(routeInfo, subject_id) {
        this.setPrimaryContent({
            xtype: 'subjectoverview',
            subject_id: subject_id
        });
    },

    showPeriod: function(routeInfo, period_id) {
        this.setPrimaryContent({
            xtype: 'periodoverview',
            period_id: period_id
        });
    },

    createNewAssignment: function(routeInfo, period_id) {
        this.breadcrumbs.set([], gettext('Create new assignment'));
        this.setPrimaryContent({
            xtype: 'createnewassignment',
            period_id: period_id
        });
    },

    createNewAssignmentSuccess: function(routeInfo) {
        this.breadcrumbs.set([], gettext('Create new assignment'));
        this.setPrimaryContent({
            xtype: 'createnewassignment-successpanel'
        });
    },

    showAssignment: function(routeInfo, assignment_id) {
        this.setPrimaryContent({
            xtype: 'assignmentoverview',
            url: routeInfo.url,
            assignment_id: assignment_id
        });
    },

    manageStudents: function(routeInfo, assignment_id) {
        this.setPrimaryContent({
            xtype: 'managestudentsoverview',
            assignment_id: assignment_id
        });
    },

    manageGroups: function(routeInfo, assignment_id) {
        this.setPrimaryContent({
            xtype: 'managestudentsoverview',
            assignment_id: assignment_id
        });
    },
    manageGroupsSelectGroups: function(routeInfo, assignment_id, group_ids) {
        this.setPrimaryContent({
            xtype: 'managestudentsoverview',
            assignment_id: assignment_id,
            select_groupids_on_load: group_ids
        });
    },
    manageGroupsAddStudents: function(routeInfo, assignment_id) {
        this.setPrimaryContent({
            xtype: 'managestudentsoverview',
            assignment_id: assignment_id,
            add_students_on_load: true
        });
    }
});
