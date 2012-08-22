Ext.define('devilry_subjectadmin.utils.UrlLookup', {
    singleton: true,

    subjectOverview: function(subject_id) {
        return Ext.String.format('#/subject/{0}/', subject_id);
    },

    periodOverview: function(period_id) {
        return Ext.String.format('#/period/{0}/', period_id);
    },
    manageRelatedStudents: function(period_id) {
        return Ext.String.format('#/period/{0}/@@manage-related-students', period_id);
    },
    manageRelatedExaminers: function(period_id) {
        return Ext.String.format('#/period/{0}/@@manage-related-examiners', period_id);
    },

    assignmentOverview: function(assignment_id) {
        return Ext.String.format('#/assignment/{0}/', assignment_id);
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

    manageDeadlines: function(assignment_id) {
        return Ext.String.format('#/assignment/{0}/@@manage-deadlines', assignment_id);
    },

    overviewByType: function(type, id) {
        if(type === 'Assignment') {
            return this.assignmentOverview(id);
        } else if(type === 'Period') {
            return this.periodOverview(id);
        } else if(type === 'Subject') {
            return this.subjectOverview(id);
        } else if(type === 'Node') {
            return '#/nodeoverview-does-not-exist-yet';
        } else {
            Ext.Error.raise({
                msg: 'The given type does not have an overview',
                type: type,
                id: id
            });
        }
    }
});
