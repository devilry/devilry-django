/**
 * Controller for the period overview.
 */
Ext.define('devilry_subjectadmin.controller.period.Overview', {
    extend: 'Ext.app.Controller',

    views: [
        'period.Overview',
        'period.ListOfAssignments'
    ],

    stores: [
        'Periods',
        'Assignments'
    ],
    models: ['Period', 'Subject'],

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
        this.period_id = this.getPeriodOverview().period_id;
        this._loadPeriod();
        this._loadAssignments();
    },

    _loadPeriod: function() {
        this.getPeriodModel().load(this.period_id, {
            callback: this._onLoadPeriod,
            scope: this
        });
    },

    _onLoadPeriod: function(record, operation) {
        if(operation.success) {
            this._onLoadPeriodSuccess(record);
        } else {
            this._onLoadFailure(operation);
        }
    },

    _onLoadFailure: function(operation) {
        var error = Ext.create('devilry_extjsextras.RestfulApiProxyErrorHandler', operation);
        error.addErrors(operation);
        this.getGlobalAlertmessagelist().addMany(error.errormessages, 'error');
    },

    _onLoadPeriodSuccess: function(record) {
        this.periodRecord = record;
        this._loadSubject();
        //this.application.fireEvent('periodSuccessfullyLoaded', record);
        this.getActions().setTitle(record.get('long_name'));
    },

    _loadSubject: function() {
        this.getSubjectModel().load(this.subject_id, {
            callback: this._onLoadSubject,
            scope: this
        });
    },

    _onLoadSubject: function(record, operation) {
        if(operation.success) {
            this._onLoadSubjectSuccess(record);
        } else {
            this._onLoadFailure(operation);
        }
    },

    _onLoadSubjectSuccess: function(record) {
        this.subjectRecord = record;
        this._setMenuLabels();
    },

    _setMenuLabels: function() {
        var periodpath = Ext.String.format('{0}.{1}',
            this.subjectRecord.get('short_name'),
            this.periodRecord.get('short_name'));
        var deleteLabel = Ext.create('Ext.XTemplate', gettext('Delete {something}')).apply({
            something: periodpath,
        });
        var renameLabel = Ext.create('Ext.XTemplate', gettext('Rename {something}')).apply({
            something: periodpath,
        });
        this.getDeleteButton().setText(deleteLabel);
        this.getRenameButton().setText(renameLabel);
    },

    _loadAssignments: function() {
        //this.getAssignmentsStore().loadAssignmentsInPeriod(this.subject_shortname, this.period_shortname, this._onLoadAssignments, this);
    },

    _onLoadAssignments: function(records, operation) {
        if(operation.success) {
        } else {
            var error = Ext.create('devilry_extjsextras.RestfulApiProxyErrorHandler', operation);
            error.addErrors(operation);
            this.getGlobalAlertmessagelist().addMany(error.errormessages, 'error');
        }
    }
});
