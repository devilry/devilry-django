/**
 * Controller for the assignment overview.
 */
Ext.define('devilry_subjectadmin.controller.assignment.Overview', {
    extend: 'Ext.app.Controller',

    mixins: {
        'loadAssignment': 'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'setBreadcrumb': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'onLoadFailure': 'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin'
    },

    views: [
        'assignment.Overview',
        'ActionList'
    ],

    models: [
        'Assignment'
    ],

    refs: [{
        ref: 'gradeEditorSidebarBox',
        selector: 'assignmentoverview editablesidebarbox[itemId=gradeeditor]'
    }, {
        ref: 'actions',
        selector: 'assignmentoverview #actions'
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
        this.assignment_id = this.getAssignmentOverview().assignment_id;
        this.loadAssignment(this.assignment_id);
    },

    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        this.application.fireEvent('assignmentSuccessfullyLoaded', record);
        this.getActions().setTitle(record.get('long_name'));
    },

    _onEditGradeEditor: function() {
        Ext.MessageBox.alert('Error', 'Not implemented yet');
    },


    onLoadAssignmentFailure: function(operation) {
        console.log('LOAD ERROR', operation);
    }
});
