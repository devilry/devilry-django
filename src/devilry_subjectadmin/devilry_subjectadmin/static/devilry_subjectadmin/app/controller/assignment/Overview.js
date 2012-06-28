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
        ref: 'globalAlertmessagelist',
        selector: 'assignmentoverview>alertmessagelist'
    }, {
        ref: 'gradeEditorSidebarBox',
        selector: 'assignmentoverview editablesidebarbox[itemId=gradeeditor]'
    }, {
        ref: 'actions',
        selector: 'assignmentoverview #actions'
    }, {
        ref: 'assignmentOverview',
        selector: 'assignmentoverview'
    }, {
        ref: 'deleteButton',
        selector: 'assignmentoverview #deleteButton'
    }, {
        ref: 'renameButton',
        selector: 'assignmentoverview #renameButton'
    }],

    init: function() {
        this.control({
            'viewport assignmentoverview': {
                render: this._onAssignmentViewRender
            },
            'viewport assignmentoverview editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            },
            'viewport assignmentoverview #deleteButton': {
                click: this._onDelete
            },
            'viewport assignmentoverview #renameButton': {
                click: this._onRename
            }
        });
    },

    _onAssignmentViewRender: function() {
        this.assignment_id = this.getAssignmentOverview().assignment_id;
        this.loadAssignment(this.assignment_id);
    },

    _getPath: function() {
        return this.getPathFromBreadcrumb(this.assignmentRecord);
    },

    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        this.application.setTitle(this._getPath());
        this.setBreadcrumb(this.assignmentRecord);
        this.getActions().setTitle(record.get('long_name'));
        this._setDangerousActionsLabels();
        this.application.fireEvent('assignmentSuccessfullyLoaded', record);
    },
    onLoadAssignmentFailure: function(operation) {
        this.onLoadFailure(operation);
    },

    _setDangerousActionsLabels: function() {
        var assignmentPath = this._getPath();
        var renameLabel = Ext.create('Ext.XTemplate', gettext('Rename {something}')).apply({
            something: assignmentPath
        });
        var deleteLabel = Ext.create('Ext.XTemplate', gettext('Delete {something}')).apply({
            something: assignmentPath
        });
        this.getRenameButton().setTitleText(renameLabel);
        this.getDeleteButton().setTitleText(deleteLabel);
    },

    _onEditGradeEditor: function() {
        Ext.MessageBox.alert('Error', 'Not implemented yet');
    },

    _onRename: function() {
        Ext.create('devilry_subjectadmin.view.RenameBasenodeWindow', {
            basenodeRecord: this.assignmentRecord
        }).show();
    },
    _onDelete: function() {
        var short_description = this._getPath();
        devilry_subjectadmin.view.DeleteDjangoRestframeworkRecordDialog.showIfCanDelete({
            basenodeRecord: this.assignmentRecord,
            short_description: short_description,
            listeners: {
                scope: this,
                deleteSuccess: function() {
                    this.application.onAfterDelete(short_description);
                }
            }
        });
    }
});
