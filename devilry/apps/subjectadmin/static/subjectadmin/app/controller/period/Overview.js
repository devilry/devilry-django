/**
 * Controller for the period overview.
 */
Ext.define('subjectadmin.controller.period.Overview', {
    extend: 'Ext.app.Controller',

    views: [
        'period.Overview',
        'period.ListOfAssignments',
        'ActionList'
    ],

    stores: [
        'Periods',
        'SingleAssignment'
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
    }],

    getAssignmentsStore: function() {
        return this.getSingleAssignmentStore();
    },

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
        this.subject_shortname = this.getPeriodOverview().subject_shortname;
        this.period_shortname = this.getPeriodOverview().period_shortname;
        this._loadPeriod();
        this._loadAssignments();
    },

    _loadPeriod: function() {
        var store = this.getPeriodsStore();
        store.loadPeriod(
            this.subject_shortname, this.period_shortname, this._onLoadPeriod, this
        );
    },

    _onLoadPeriod: function(records, operation) {
        if(operation.success) {
            this._onLoadPeriodSuccess(records[0]);
        } else {
            this._onLoadPeriodFailure(operation);
        }
    },

    _onLoadPeriodFailure: function(operation) {
        var error = Ext.create('themebase.RestfulApiProxyErrorHandler', operation);
        error.addErrors(operation);
        this.getGlobalAlertmessagelist().addMany(error.errormessages, 'error');
    },

    _onLoadPeriodSuccess: function(record) {
        this.assignmentRecord = record;
        //this.application.fireEvent('periodSuccessfullyLoaded', record);
        this.getActions().setTitle(record.get('long_name'));
    },

    _loadAssignments: function() {
        this.getAssignmentsStore().loadAssignmentsInPeriod(this.subject_shortname, this.period_shortname, this._onLoadAssignments, this);
    },

    _onLoadAssignments: function(records, operation) {
        if(operation.success) {
            
        } else {
            var error = Ext.create('themebase.RestfulApiProxyErrorHandler', operation);
            error.addErrors(operation);
            this.getAlertmessagelist().addMany(error.errormessages, 'error');
        }
    }
});
