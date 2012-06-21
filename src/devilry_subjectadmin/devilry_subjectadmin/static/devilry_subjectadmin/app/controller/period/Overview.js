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
    models: ['Period'],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'periodoverview>alertmessagelist'
    }, {
        ref: 'actions',
        selector: 'periodoverview #actions'
    }, {
        ref: 'periodOverview',
        selector: 'periodoverview'
    }],

    init: function() {
        this.control({
            'viewport periodoverview': {
                render: this._onPeriodViewRender
            },
            'viewport periodoverview editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            }
        });
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
            this._onLoadPeriodFailure(operation);
        }
    },

    _onLoadPeriodFailure: function(operation) {
        var error = Ext.create('devilry_extjsextras.RestfulApiProxyErrorHandler', operation);
        error.addErrors(operation);
        this.getGlobalAlertmessagelist().addMany(error.errormessages, 'error');
    },

    _onLoadPeriodSuccess: function(record) {
        this.periodRecord = record;
        //this.application.fireEvent('periodSuccessfullyLoaded', record);
        this.getActions().setTitle(record.get('long_name'));
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
