/**
 * Controller for the period overview.
 */
Ext.define('devilry_subjectadmin.controller.period.Overview', {
    extend: 'Ext.app.Controller',

    mixins: {
        'loadSubject': 'devilry_subjectadmin.utils.LoadSubjectMixin',
        'loadPeriod': 'devilry_subjectadmin.utils.LoadPeriodMixin'
    },

    views: [
        'period.Overview',
        'period.ListOfAssignments'
    ],

    stores: [
        'Periods',
        'Assignments'
    ],
    models: ['Period', 'Subject'],

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
        this._setBreadcrumbs([], gettext('Loading ...'));
        this.period_id = this.getPeriodOverview().period_id;
        this.loadPeriod(this.period_id);
        this._loadAssignments();
    },

    _setBreadcrumbs: function(breadcrumbsExtra, current) {
        var breadcrumbsBase = [{
            text: gettext("All subjects"),
            url: '/'
        }];
        var breadcrumbs = breadcrumbsBase.concat(breadcrumbsExtra);
        this.application.breadcrumbs.set(breadcrumbs, current);
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
    },

    _onLoadFailure: function(operation) {
        var error = Ext.create('devilry_extjsextras.RestfulApiProxyErrorHandler', operation);
        error.addErrors(operation);
        this.getGlobalAlertmessagelist().addMany(error.errormessages, 'error');
    },

    /** Implement methods required by LoadSubjectMixin */
    onLoadSubjectSuccess: function(record) {
        this.subjectRecord = record;
        this._setBreadcrumbs([{
            text: this.subjectRecord.get('short_name'),
            url: devilry_subjectadmin.utils.UrlLookup.subjectOverview(this.subjectRecord.get('id'))
        }], this.periodRecord.get('short_name'));
        this._setMenuLabels();
    },
    onLoadSubjectFailure: function(operation) {
        this._onLoadFailure(operation);
    },

    /** Implement methods required by LoadPeriodMixin */
    onLoadPeriodSuccess: function(record) {
        this.periodRecord = record;
        this.loadSubject(this.periodRecord.get('parentnode'));
        //this.application.fireEvent('periodSuccessfullyLoaded', record);
        this.getActions().setTitle(record.get('long_name'));
    },
    onLoadPeriodFailure: function(operation) {
        this._onLoadFailure(operation);
    }
});
