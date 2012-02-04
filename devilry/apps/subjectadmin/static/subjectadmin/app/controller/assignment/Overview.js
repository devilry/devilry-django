/**
 * Controller for the assignment overview.
 */
Ext.define('subjectadmin.controller.assignment.Overview', {
    extend: 'Ext.app.Controller',

    mixins: {
        'loadAssignment': 'subjectadmin.utils.LoadAssignmentMixin'
    },

    views: [
        'assignment.Overview',
        'ActionList'
    ],

    stores: [
        'SingleAssignment'
    ],

    refs: [{
        ref: 'gradeEditorSidebarBox',
        selector: 'editablesidebarbox[itemId=gradeeditor]'
    }, {
        ref: 'primaryTitle',
        selector: 'centertitle[itemId=primaryTitle]'
    }, {
        ref: 'assignmentOverview',
        selector: 'assignmentoverview'
    }],

    init: function() {
        this.control({
            'viewport assignmentoverview': {
                render: this._onAssignmentViewRender
            },
            'viewport assignmentoverview editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            }
        });
    },

    _onAssignmentViewRender: function() {
        this.subject_shortname = this.getAssignmentOverview().subject_shortname;
        this.period_shortname = this.getAssignmentOverview().period_shortname;
        this.assignment_shortname = this.getAssignmentOverview().assignment_shortname;
        this.loadAssignment();
    },

    getSubjectShortname: function() {
        return this.subject_shortname;
    },
    getPeriodShortname: function() {
        return this.period_shortname;
    },
    getAssignmentShortname: function() {
        return this.assignment_shortname;
    },

    getMaskElement: function() {
        return this.getAssignmentOverview().getEl();
    },

    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        this.application.fireEvent('assignmentSuccessfullyLoaded', record);
        this.getPrimaryTitle().update(record.get('long_name'));
    },

    _onEditGradeEditor: function() {
        console.log('grade', this.getGradeEditorSidebarBox());
    }
});
