/**
 * Controller for the assignment overview.
 */
Ext.define('devilry_subjectadmin.controller.assignment.AssignmentController', {
    extend: 'Ext.app.Controller',

    mixins: {
        'loadAssignment': 'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'setBreadcrumb': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'onLoadFailure': 'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin'
    },

    views: [
        'assignment.AssignmentOverview'
    ],

    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    models: [
        'Assignment'
    ],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
    }, {
        ref: 'header',
        selector: 'assignmentoverview #header'
    }, {
        ref: 'assignmentOverview',
        selector: 'assignmentoverview'
    }, {
        ref: 'deleteButton',
        selector: 'assignmentoverview #deleteButton'
    }, {
        ref: 'renameButton',
        selector: 'assignmentoverview #renameButton'
    }, {
        ref: 'noGroupsMessage',
        selector: 'assignmentoverview #noGroupsMessage'
    }, {
        ref: 'adminsbox',
        selector: 'assignmentoverview adminsbox'
    }, {
        ref: 'linkList',
        selector: 'assignmentoverview #linkList'
    }, {
        ref: 'examinerRoleBox',
        selector: 'assignmentoverview #examinerRoleBox'
    }, {
        ref: 'betaFeaturesBox',
        selector: 'assignmentoverview #betaFeaturesBox'
    }],

    init: function() {
        this.control({
            'viewport assignmentoverview': {
                render: this._onAssignmentViewRender
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
        this.getHeader().update({
            heading: record.get('long_name')
        });
        this._setDangerousActionsLabels();
        this.application.fireEvent('assignmentSuccessfullyLoaded', record);
        if(this.assignmentRecord.get('number_of_groups') === 0) {
            this._handleNoGroups();
        } else {
            this._updateLinkList(true);
            this._updateExaminerBox();
            this._updateBetaFeaturesBox();
        }
        this.getAdminsbox().setBasenodeRecord(this.assignmentRecord);
    },
    onLoadAssignmentFailure: function(operation) {
        this.onLoadFailure(operation);
    },

    _isElectronic: function() {
        return this.assignmentRecord.get('delivery_types') === 0;
    },
    

    _updateLinkList: function(has_students) {
        this.getLinkList().update({
            managestudents_url: devilry_subjectadmin.utils.UrlLookup.manageStudents(this.assignment_id),
            managedeadlines_url: devilry_subjectadmin.utils.UrlLookup.bulkManageDeadlines(this.assignment_id),
            passedpreviousperiod_url: devilry_subjectadmin.utils.UrlLookup.passedPreviousPeriod(this.assignment_id),
            examinerstats_url: devilry_subjectadmin.utils.UrlLookup.assignmentExaminerStats(this.assignment_id),
            assignmentData: this.assignmentRecord.data,
            electronic: this._isElectronic(),
            period_term: gettext('period'),
            has_students: has_students
        });
    },

    _updateExaminerBox: function() {
        this.getExaminerRoleBox().updateData({
            loading: false,
            is_published: this.assignmentRecord.get('is_published'),
            mygroupscount: this.assignmentRecord.get('number_of_groups_where_is_examiner'),
            totalgroups: this.assignmentRecord.get('number_of_groups'),
            examinerui_url: devilry_subjectadmin.utils.UrlLookup.examinerGroupsOverviewTodo(this.assignmentRecord.get('id'))
        });
    },

    _updateBetaFeaturesBox: function() {
        this.getBetaFeaturesBox().update({
            loading: false,
            detektor_assemblyview_url: devilry_subjectadmin.utils.UrlLookup.detektorAdminAssemblyView(this.assignmentRecord.get('id'))
        });
    },

    _setDangerousActionsLabels: function() {
        var assignmentPath = this._getPath();

        if(this.assignmentRecord.get('can_delete')) {
            var deleteLabel = Ext.create('Ext.XTemplate', gettext('Delete {something}')).apply({
                something: assignmentPath
            });
            this.getDeleteButton().setTitleText(deleteLabel);
            this.getDeleteButton().show();
        }

        var renameLabel = Ext.create('Ext.XTemplate', gettext('Rename {something}')).apply({
            something: assignmentPath
        });
        this.getRenameButton().setTitleText(renameLabel);
    },

    _onRename: function() {
        window.location.href = devilry_subjectadmin.utils.UrlLookup.updateAssignment(this.assignment_id);
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
    },

    _handleNoGroups: function() {
        this.getNoGroupsMessage().show();
        this.getExaminerRoleBox().hide();
        this._updateLinkList(false);
    }
});
