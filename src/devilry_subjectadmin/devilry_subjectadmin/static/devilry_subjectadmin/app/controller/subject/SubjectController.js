/**
 * Controller for the subject overview.
 */
Ext.define('devilry_subjectadmin.controller.subject.SubjectController', {
    extend: 'Ext.app.Controller',
    mixins: {
        'setBreadcrumb': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'onLoadFailure': 'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin'
    },

    views: [
        'subject.SubjectOverview',
        'subject.ListOfPeriods',
        'RenameBasenodeWindow',
        'DeleteDjangoRestframeworkRecordDialog'
    ],

    requires: [
        'devilry_extjsextras.ConfirmDeleteDialog'
    ],

    stores: ['Periods'],
    models: ['Subject'],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
    }, {
        ref: 'deleteButton',
        selector: 'subjectoverview #deleteButton'
    }, {
        ref: 'renameButton',
        selector: 'subjectoverview #renameButton'
    }, {
        ref: 'header',
        selector: 'subjectoverview #header'
    }, {
        ref: 'subjectOverview',
        selector: 'subjectoverview'
    }, {
        ref: 'adminsbox',
        selector: 'subjectoverview adminsbox'
    }],

    init: function() {
        this.control({
            'viewport subjectoverview': {
                render: this._onSubjectViewRender
            },
            'viewport subjectoverview #deleteButton': {
                click: this._onDelete
            },
            'viewport subjectoverview #renameButton': {
                click: this._onRename
            }
        });
    },

    _onNotImplemented: function() {
        Ext.MessageBox.alert('Unavailable', 'Not implemented yet');
    },

    _onSubjectViewRender: function() {
        this.setLoadingBreadcrumb();
        this.subject_id = this.getSubjectOverview().subject_id;
        this._loadSubject(this.subject_id);
        this._loadPeriods();
    },

    _setDangerousActionsLabels: function() {
        if(this.subjectRecord.get('can_delete')) {
            var deleteLabel = Ext.create('Ext.XTemplate', gettext('Delete {something}')).apply({
                something: this.subjectRecord.get('short_name')
            });
            this.getDeleteButton().setTitleText(deleteLabel);
            this.getDeleteButton().show();
        }

        var renameLabel = Ext.create('Ext.XTemplate', gettext('Rename {something}')).apply({
            something: this.subjectRecord.get('short_name')
        });
        this.getRenameButton().setTitleText(renameLabel);
    },

    _loadPeriods: function() {
        this.getPeriodsStore().loadPeriodsInSubject(this.subject_id, this._onLoadPeriods, this);
    },

    _onLoadPeriods: function(records, operation) {
        if(operation.success) {
            
        } else {
            this.onLoadFailure(operation);
        }
    },

    _loadSubject: function(subject_id) {
        this.getSubjectModel().load(subject_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this._onLoadSubjectSuccess(record);
                } else {
                    this.onLoadFailure(operation);
                }
            }
        });
    },
    _onLoadSubjectSuccess: function(record) {
        this.subjectRecord = record;
        this.application.setTitle(this.subjectRecord.get('short_name'));
        this.getHeader().update({
            heading: record.get('long_name')
        });
        this.setBreadcrumb(this.subjectRecord);
        this.getAdminsbox().setBasenodeRecord(this.subjectRecord);
        this._setDangerousActionsLabels();
    },

    _onRename: function() {
        Ext.create('devilry_subjectadmin.view.RenameBasenodeWindow', {
            basenodeRecord: this.subjectRecord
        }).show();
    },
    _onDelete: function() {
        var short_description = this.subjectRecord.get('short_name');
        devilry_subjectadmin.view.DeleteDjangoRestframeworkRecordDialog.showIfCanDelete({
            basenodeRecord: this.subjectRecord,
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
