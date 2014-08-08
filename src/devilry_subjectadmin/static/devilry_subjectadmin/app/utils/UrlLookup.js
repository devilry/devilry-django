Ext.define('devilry_subjectadmin.utils.UrlLookup', {
    singleton: true,

    subjectOverview: function(subject_id) {
        return Ext.String.format('#/subject/{0}/', subject_id);
    },
    createNewPeriod: function(period_id) {
        return Ext.String.format('#/subject/{0}/@@create-new-period', period_id);
    },

    periodOverview: function(period_id) {
        return Ext.String.format('#/period/{0}/', period_id);
    },
    createNewAssignment: function(period_id, options) {
        var optionstring = '';
        if(options) {
            optionstring = Ext.Object.toQueryString(options);
        }
        return Ext.String.format('#/period/{0}/@@create-new-assignment/{1}', period_id, optionstring);
    },
    manageRelatedStudents: function(period_id) {
        return Ext.String.format('#/period/{0}/@@relatedstudents', period_id);
    },
    manageRelatedExaminers: function(period_id) {
        return Ext.String.format('#/period/{0}/@@relatedexaminers', period_id);
    },
    detailedPeriodOverview: function(period_id) {
        return Ext.String.format('#/period/{0}/@@detailedoverview', period_id);
    },

    assignmentOverview: function(assignment_id) {
        return Ext.String.format('#/assignment/{0}/', assignment_id);
    },

    editGradeEditor: function(assignment_id) {
        return Ext.String.format('{0}/devilry_gradingsystem/admin/summary/{1}',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX,
            assignment_id);
    },

    passedPreviousPeriod: function(assignment_id) {
        return Ext.String.format('#/assignment/{0}/@@passed-previous-period', assignment_id);
    },
    assignmentExaminerStats: function(assignment_id) {
        return Ext.String.format('#/assignment/{0}/@@examinerstats', assignment_id);
    },

    manageStudents: function(assignment_id) {
        return Ext.String.format('#/assignment/{0}/@@manage-students/', assignment_id);
    },

    manageSpecificGroups: function(assignment_id, group_ids) {
        var prefix = this.manageSpecificGroupsPrefix(assignment_id);
        return Ext.String.format('{0}{1}', prefix, group_ids.join(','));
    },
    manageSpecificGroupsPrefix: function(assignment_id) {
        return Ext.String.format('#/assignment/{0}/@@manage-students/@@select/', assignment_id);
    },
    manageStudentsAddStudents: function(assignment_id) {
        return Ext.String.format('#/assignment/{0}/@@manage-students/@@add-students', assignment_id);
    },
    manageGroupAndShowDeliveryPrefix: function(assignment_id, group_id) {
        return Ext.String.format('#/assignment/{0}/@@manage-students/@@select-delivery/{1}/',
            assignment_id, group_id);
    },

    bulkManageDeadlines: function(assignment_id) {
        return Ext.String.format('#/assignment/{0}/@@bulk-manage-deadlines/', assignment_id);
    },
    bulkManageAddDeadlines: function(assignment_id) {
        return this.bulkManageDeadlines(assignment_id) + '@@add';
    },
    bulkManageSpecificDeadline: function(assignment_id, bulkdeadline_id) {
        var prefix = this.bulkManageDeadlines(assignment_id);
        return Ext.String.format('{0}{1}', prefix, bulkdeadline_id);
    },
    bulkEditSpecificDeadline: function(assignment_id, bulkdeadline_id) {
        var prefix = this.bulkManageDeadlines(assignment_id);
        return Ext.String.format('{0}@@edit/{1}', prefix, bulkdeadline_id);
    },

    overviewByType: function(type, id) {
        if(type === 'Assignment') {
            return this.assignmentOverview(id);
        } else if(type === 'Period') {
            return this.periodOverview(id);
        } else if(type === 'Subject') {
            return this.subjectOverview(id);
        } else if(type === 'Node') {
            return this.nodeadminNodeOverview(id);
        } else {
            Ext.Error.raise({
                msg: 'The given type does not have an overview',
                type: type,
                id: id
            });
        }
    },


    updateAssignment: function(assignment_id) {
        return Ext.String.format('{0}/devilry_subjectadmin/assignment/{1}/update',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX,
            assignment_id);
    },


    //
    //
    // In the nodeadmin UI
    //
    //
    //
    nodeadminNodeOverview: function(node_pk) {
        return Ext.String.format('{0}/devilry_nodeadmin/#/node/{1}',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX,
            node_pk);
    },
    nodeadminDashboard: function() {
        return Ext.String.format('{0}/devilry_nodeadmin/',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX);
    },

    //
    //
    // In the examiner UI
    //
    //
    //
    examinerGroupOverview: function(group_id) {
        return Ext.String.format('{0}/devilry_examiner/singlegroupoverview/{1}',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX,
            group_id);
    },
    examinerGroupsOverviewTodo: function(assignment_id) {
        return Ext.String.format('{0}/devilry_examiner/allgroupsoverview/{1}',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX,
            assignment_id);
    },
    examinerGroupsOverviewStudents: function(assignment_id) {
        return this.examinerGroupsOverviewTodo(assignment_id);
    }
});
