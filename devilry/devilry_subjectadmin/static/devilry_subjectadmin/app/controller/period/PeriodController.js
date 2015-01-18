/**
 * Controller for the period overview.
 */
Ext.define('devilry_subjectadmin.controller.period.PeriodController', {
    extend: 'Ext.app.Controller',

    mixins: {
        'setBreadcrumb': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'onLoadFailure': 'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin'
    },

    views: [
        'period.PeriodOverview',
        'period.ListOfAssignments'
    ],

    stores: ['Assignments', 'RelatedExaminers', 'RelatedStudents'],
    models: ['Period'],

    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: '#appAlertmessagelist'
    }, {
        ref: 'header',
        selector: 'periodoverview #header'
    }, {
        ref: 'periodOverview',
        selector: 'periodoverview'
    }, {
        ref: 'deleteButton',
        selector: 'periodoverview #deleteButton'
    }, {
        ref: 'renameButton',
        selector: 'periodoverview #renameButton'
    }, {
        ref: 'adminsbox',
        selector: 'periodoverview adminsbox'
    }, {
        ref: 'createNewAssignmentBox',
        selector: 'periodoverview #createNewAssignmentBox'
    }, {
        ref: 'noRelatedStudentsMessage',
        selector: 'periodoverview #noRelatedStudentsMessage'
    }, {
        ref: 'noRelatedExaminersMessage',
        selector: 'periodoverview #noRelatedExaminersMessage'
    }],

    init: function() {
        this.control({
            'viewport periodoverview': {
                render: this._onPeriodViewRender
            },
            'viewport periodoverview #deleteButton': {
                click: this._onDelete
            },
            'viewport periodoverview #renameButton': {
                click: this._onRename
            }
        });
    },

    _getPath: function() {
        return this.getPathFromBreadcrumb(this.periodRecord);
    },

    _onPeriodViewRender: function() {
        this.setLoadingBreadcrumb();
        this.period_id = this.getPeriodOverview().period_id;
        this._loadPeriod(this.period_id);
        this._loadAssignments(this.period_id);
    },

    _setMenuLabels: function() {
        var periodpath = this._getPath();

        if(this.periodRecord.get('can_delete')) {
            var deleteLabel = Ext.create('Ext.XTemplate', gettext('Delete {something}')).apply({
                something: periodpath
            });
            this.getDeleteButton().setTitleText(deleteLabel);
            this.getDeleteButton().show();
        }

        var renameLabel = Ext.create('Ext.XTemplate', gettext('Rename {something}')).apply({
            something: periodpath
        });
        this.getRenameButton().setTitleText(renameLabel);
    },

    _loadAssignments: function(period_id) {
        this.getAssignmentsStore().loadAssignmentsInPeriod(period_id, this._onLoadAssignments, this);
    },

    _onLoadAssignments: function(records, operation) {
        if(operation.success) {
        } else {
            this.onLoadFailure(operation);
        }
    },

    _loadPeriod: function(period_id) {
        this.getPeriodModel().load(period_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this._onLoadPeriodSuccess(record);
                } else {
                    this._onLoadPeriodFailure(operation);
                }
            }
        });
    },
    _onLoadPeriodSuccess: function(record) {
        this.periodRecord = record;
        this.application.fireEvent('periodSuccessfullyLoaded', record);
        this.application.setTitle(this._getPath());
        this.getHeader().update({
            period: record.get('long_name'),
            subject: record.get('breadcrumb')[0].text
        });
        this.setBreadcrumb(this.periodRecord);
        this._setMenuLabels();
        this.getAdminsbox().setBasenodeRecord(this.periodRecord);
        if(this.periodRecord.get('number_of_relatedstudents') === 0) {
            this._handleNoRelatedStudents();
        }
        if(this.periodRecord.get('number_of_relatedexaminers') === 0) {
            this._handleNoRelatedExaminers();
        }
    },
    _onLoadPeriodFailure: function(operation) {
        this.onLoadFailure(operation);
    },

    _onRename: function() {
        Ext.create('devilry_subjectadmin.view.RenameBasenodeWindow', {
            basenodeRecord: this.periodRecord
        }).show();
    },
    _onDelete: function() {
        var short_description = this._getPath();
        devilry_subjectadmin.view.DeleteDjangoRestframeworkRecordDialog.showIfCanDelete({
            basenodeRecord: this.periodRecord,
            short_description: short_description,
            listeners: {
                scope: this,
                deleteSuccess: function() {
                    this.application.onAfterDelete(short_description);
                }
            }
        });
    },


    _handleNoRelatedStudents: function() {
        this.getCreateNewAssignmentBox().hide();
        this.getNoRelatedStudentsMessage().show();
    },
    _handleNoRelatedExaminers: function() {
        this.getNoRelatedExaminersMessage().show();
    }
});
