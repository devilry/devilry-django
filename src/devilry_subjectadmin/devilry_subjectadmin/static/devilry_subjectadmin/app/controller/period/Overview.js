/**
 * Controller for the period overview.
 */
Ext.define('devilry_subjectadmin.controller.period.Overview', {
    extend: 'Ext.app.Controller',

    mixins: {
        'setBreadcrumb': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'onLoadFailure': 'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin'
    },

    views: [
        'period.Overview',
        'period.ListOfAssignments'
    ],

    stores: ['Assignments'],
    models: ['Period'],

    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'periodoverview>alertmessagelist'
    }, {
        ref: 'actions',
        selector: 'periodoverview #actions'
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
        ref: 'basenodehierlocation',
        selector: 'periodoverview basenodehierlocation'
    }],

    init: function() {
        this.control({
            'viewport periodoverview': {
                render: this._onPeriodViewRender
            },
            'viewport periodoverview editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            },
            'viewport periodoverview #deleteButton': {
                click: this._onNotImplemented
            },
            'viewport periodoverview #renameButton': {
                click: this._onNotImplemented
            }
        });
    },

    _onNotImplemented: function() {
        Ext.MessageBox.alert('Unavailable', 'Not implemented yet');
    },

    _onPeriodViewRender: function() {
        this.setLoadingBreadcrumb();
        this.period_id = this.getPeriodOverview().period_id;
        this._loadPeriod(this.period_id);
        this._loadAssignments(this.period_id);
    },

    _setBreadcrumbs: function(breadcrumbsExtra, current) {
        var breadcrumbsBase = [{
            text: gettext("All subjects"),
            url: '/'
        }];
        var breadcrumbs = breadcrumbsBase.concat(breadcrumbsExtra);
        this.application.breadcrumbs.set(breadcrumbs, current);
    },

    _setMenuLabels: function(periodpath) {
        var deleteLabel = Ext.create('Ext.XTemplate', gettext('Delete {something}')).apply({
            something: periodpath,
        });
        var renameLabel = Ext.create('Ext.XTemplate', gettext('Rename {something}')).apply({
            something: periodpath,
        });
        this.getDeleteButton().setText(deleteLabel);
        this.getRenameButton().setText(renameLabel);
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

    _loadPeriod: function(subject_id) {
        this.getPeriodModel().load(subject_id, {
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
        var periodpath = this.getPathFromBreadcrumb(this.periodRecord);
        //this.application.fireEvent('periodSuccessfullyLoaded', record);
        this.getActions().setTitle(record.get('long_name'));
        this.setBreadcrumb(this.periodRecord);
        this._setMenuLabels(periodpath);
        this.getAdminsbox().setBasenodeRecord(this.periodRecord, periodpath);
        this.getBasenodehierlocation().setLocation(this.periodRecord);
    },
    _onLoadPeriodFailure: function(operation) {
        this.onLoadFailure(operation);
    }
});
