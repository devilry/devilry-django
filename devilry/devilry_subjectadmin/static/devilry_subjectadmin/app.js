var querystring = Ext.Object.fromQueryString(window.location.search);
if(Ext.isEmpty(querystring.routeTo)) {
    Ext.application({
        name: 'devilry_subjectadmin',
        appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_subjectadmin/app',
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
            'Ext.layout.container.Border',
            'Ext.layout.container.Column',
            'Ext.layout.container.Card',
            'Ext.form.RadioGroup',
            'Ext.form.field.Radio',
            'Ext.util.Cookies',
            'devilry_extjsextras.Router',
            'devilry_extjsextras.RouteNotFound',
            'devilry_extjsextras.AlertMessage',
            'devilry_header.Header2',
            'devilry_subjectadmin.utils.Breadcrumbs',
            'devilry_subjectadmin.utils.UrlLookup',
            'devilry_extjsextras.form.DateField',
            'devilry_extjsextras.form.TimeField',
            'devilry_extjsextras.FloatingAlertmessageList',
            'devilry_authenticateduserinfo.UserInfo'
        ],

        controllers: [
            'Dashboard',
            'CreateNewAssignment',
            'subject.ListAll',
            'subject.SubjectController',
            'period.PeriodController',
            'period.EditDuration',
            'CreateNewPeriod',
            'assignment.AssignmentController',
            'assignment.EditPublishingTime',
            'assignment.EditAnonymous',
            'assignment.EditDeadlineHandling',
            'assignment.EditGradeEditor',
            'managestudents.ManageStudentsController',
            'managestudents.Select',
            'managestudents.NoGroupSelectedViewPlugin',
            'managestudents.SingleGroupSelectedViewPlugin',
            'managestudents.MultipleGroupsSelectedViewPlugin',
            'AddGroups',
            'AllWhereIsAdmin',
            'BulkManageDeadlines',
            'RelatedStudents',
            'RelatedExaminers',
            'PassedPreviousPeriodController',
            'DetailedPeriodOverviewController',
            'ExaminerStatsController',

            'GuideSystem',
            'guides.CreateNewAssignment',
            'guides.QualifiedForFinalExams'
        ],

        refs: [{
            ref: 'alertmessagelist',
            selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
        }],

        constructor: function() {
            this.addEvents(
               /**
                 * @event
                 * Fired when a period is successfully loaded by the period.Period.
                 * @param {devilry_subjectadmin.model.Period} periodRecord 
                 */
                'periodSuccessfullyLoaded',

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
                'managestudentsGroupSorterChanged',


                /**
                 * @event
                 * Forwarded from the Router, primarily to make it possible for controllers to attach to route events before the router object is created.
                 */
                'beforeroute',

                /**
                 * @event
                 * Forwarded from the Router, primarily to make it possible for controllers to attach to route events before the router object is created.
                 */
                'afterroute'
            );
            this.callParent(arguments);
        },

        launch: function() {
            this._createViewport();
        },

        _createViewport: function() {
            this.viewport = Ext.create('Ext.container.Viewport', {
                xtype: 'container',
                layout: 'border'
            });
            this.viewport.setLoading();
            devilry_authenticateduserinfo.UserInfo.load(this._onUserInfoLoaded, this);
        },

        _onUserInfoLoaded: function(userInfoRecord) {
            this.userInfoRecord = userInfoRecord;
            this.breadcrumbs = Ext.create('devilry_subjectadmin.utils.Breadcrumbs');
            this.primaryContentContainer = Ext.widget('container', {
                region: 'center',
                layout: 'fit'
            });
            this.viewport.removeAll();
            this.viewport.add([{
                xtype: 'devilryheader2',
                region: 'north',
                navclass: this.userInfoRecord.isSubjectPeriodOrAssignmentAdmin()? 'subjectadmin': 'nodeadmin',
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
            }, {
                xtype: 'guidesystemview',
                region: 'east',
                hidden: true,
                width: 220
            }]);
            this.viewport.setLoading(false);
            this._onViewportReady();
        },

        _onViewportReady: function() {
            this._setupRoutes();
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

        /**
         * Controllers can use this to add alertmessages that will be shown on the
         * next route, right after the ``beforeroute`` event has fired.
         * */
        addOnNextRouteMessage: function(config) {
            if(!this._hasOnNextRouteMessages()) {
                this.onNextRouteMessages = [];
            }
            this.onNextRouteMessages.push(config);
        },

        _hasOnNextRouteMessages: function() {
            return !Ext.isEmpty(this.onNextRouteMessages);
        },
        _showOnNextRouteMessages: function() {
            this.getAlertmessagelist().addArray(this.onNextRouteMessages);
            this.onNextRouteMessages = undefined;
        },


        /*********************************************
         * Routing
         ********************************************/

        _setupRoutes: function() {
            this.route = Ext.create('devilry_extjsextras.Router', this, {
                listeners: {
                    scope: this,
                    beforeroute: this._beforeRoute,
                    afterroute: this._afterRoute
                }
            });
            this.route.add("", 'dashboard');
            this.route.add("/allsubjects/", 'allSubjects');
            this.route.add("/", 'allWhereIsAdmin');
            this.route.add("/subject/:subject_id/", 'showSubject');
            this.route.add("/subject/:subject_id/@@create-new-period", 'createNewPeriod');
            this.route.add("/period/:period_id/", 'showPeriod');
            this.route.add("/period/:period_id/@@relatedstudents", 'showRelatedStudents');
            this.route.add("/period/:period_id/@@relatedexaminers", 'showRelatedExaminers');
            this.route.add("/period/:period_id/@@detailedoverview", 'detailedPeriodOverview');
            this.route.add("/period/:period_id/@@create-new-assignment/", 'createNewAssignment');
            this.route.add("/period/:period_id/@@create-new-assignment/:defaults", 'createNewAssignment');
            this.route.add("/assignment/:assignment_id/", 'showAssignment');
            this.route.add("/assignment/:assignment_id/@@manage-students/", 'manageStudents');
            this.route.add("/assignment/:assignment_id/@@examinerstats", 'examinerstats');
            this.route.add("/assignment/:assignment_id/@@manage-students/@@select-delivery/:group_id/:delivery_id", 'manageGroupsSelectDelivery');
            this.route.add("/assignment/:assignment_id/@@manage-students/@@select/:group_ids", 'manageGroupsSelectGroups');
            this.route.add("/assignment/:assignment_id/@@manage-students/@@add-students", 'manageGroupsAddStudents');
            this.route.add("/assignment/:assignment_id/@@bulk-manage-deadlines/", 'bulkManageDeadlines');
            this.route.add("/assignment/:assignment_id/@@bulk-manage-deadlines/@@edit/:bulkdeadline_id", 'bulkEditDeadlines');
            this.route.add("/assignment/:assignment_id/@@bulk-manage-deadlines/@@add", 'bulkAddDeadlines');
            this.route.add("/assignment/:assignment_id/@@bulk-manage-deadlines/:bulkdeadline_id", 'bulkManageDeadlines');
            this.route.add("/assignment/:assignment_id/@@passed-previous-period", 'passedPreviousPeriod');
            this.route.start();
        },

        _beforeRoute: function(route, routeInfo) {
            this.getAlertmessagelist().removeAll();
            this.fireEvent('beforeroute', route, routeInfo);
            if(this._hasOnNextRouteMessages()) {
                this._showOnNextRouteMessages();
            }
        },
        _afterRoute: function(route, routeInfo) {
            this.fireEvent('afterroute', route, routeInfo);
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

        allSubjects: function(routeInfo) {
            this.breadcrumbs.set([], gettext("All my courses"));
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

        createNewPeriod: function(routeInfo, subject_id) {
            this.setPrimaryContent({
                xtype: 'createnewperiod',
                subject_id: subject_id
            });
        },

        showPeriod: function(routeInfo, period_id) {
            this.setPrimaryContent({
                xtype: 'periodoverview',
                period_id: period_id
            });
        },
        showRelatedStudents: function(routeInfo, period_id) {
            this.setPrimaryContent({
                xtype: 'relatedstudents',
                period_id: period_id
            });
        },
        showRelatedExaminers: function(routeInfo, period_id) {
            this.setPrimaryContent({
                xtype: 'relatedexaminers',
                period_id: period_id
            });
        },
        detailedPeriodOverview: function(routeInfo, period_id) {
            this.setPrimaryContent({
                xtype: 'detailedperiodoverview',
                period_id: period_id
            });
        },

        passedPreviousPeriod: function(routeInfo, assignment_id) {
            this.setPrimaryContent({
                xtype: 'passedpreviousperiodoverview',
                assignment_id: assignment_id
            });
        },

        createNewAssignment: function(routeInfo, period_id, defaults) {
            this.setPrimaryContent({
                xtype: 'createnewassignment',
                period_id: period_id,
                defaults: defaults
            });
        },

        showAssignment: function(routeInfo, assignment_id) {
            this.setPrimaryContent({
                xtype: 'assignmentoverview',
                url: routeInfo.url,
                assignment_id: assignment_id
            });
        },

        examinerstats: function(routeInfo, assignment_id) {
            this.setPrimaryContent({
                xtype: 'examinerstatsoverview',
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
        manageGroupsSelectDelivery: function(routeInfo, assignment_id, group_id, delivery_id) {
            this.setPrimaryContent({
                xtype: 'managestudentsoverview',
                assignment_id: assignment_id,
                select_groupids_on_load: group_id,
                select_delivery_on_load: delivery_id
            });
        },
        manageGroupsAddStudents: function(routeInfo, assignment_id) {
            this.setPrimaryContent({
                xtype: 'addgroupsoverview',
                assignment_id: assignment_id,
                on_save_success_url: devilry_subjectadmin.utils.UrlLookup.manageStudents(assignment_id),
                breadcrumbtype: 'managestudents'
            });
        },

        bulkManageDeadlines: function(routeInfo, assignment_id, bulkdeadline_id, edit_deadline, add_deadline) {
            this.setPrimaryContent({
                xtype: 'bulkmanagedeadlinespanel',
                assignment_id: assignment_id,
                bulkdeadline_id: bulkdeadline_id,
                edit_deadline: edit_deadline,
                add_deadline: add_deadline
            });
        },
        bulkEditDeadlines: function(routeInfo, assignment_id, bulkdeadline_id) {
            this.bulkManageDeadlines(routeInfo, assignment_id, bulkdeadline_id, true);
        },
        bulkAddDeadlines: function(routeInfo, assignment_id) {
            this.bulkManageDeadlines(routeInfo, assignment_id, undefined, false, true);
        },

        allWhereIsAdmin: function() {
            this.setPrimaryContent({
                xtype: 'allwhereisadminpanel'
            });
        }
    });
} else {
    /*
    If the user goes to ``/devilry_subjectadmin/?routeTo=/some/path``, we want to
    redirect them to ``/devilry_subjectadmin/#/some/path``. We need this functionality
    because we want to create Django redirect views with a named URL for linking from
    Django templates into devilry_subjectadmin.

    This, along with ``devilry_subjectadmin.utils.UrlLookup`` makes it much easier to
    migrate devilry_subjectadmin pages to regular Django template based views because
    we only have to replace the view with the redirect view, and update UrlLookup,
    instead of updating all the pages linking to the new view.
    */
    var newUrl = Ext.String.format('{0}/devilry_subjectadmin/#{1}',
        window.DevilrySettings.DEVILRY_URLPATH_PREFIX,
        querystring.routeTo);
    window.location = newUrl;
}
