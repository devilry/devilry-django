/**
 * Controller for the period overview.
 */
Ext.define('subjectadmin.controller.period.Overview', {
    extend: 'Ext.app.Controller',

    views: [
        'period.Overview',
        'ActionList'
    ],

    stores: [
        'Periods'
    ],

    refs: [{
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
        this.period_shortname = this.getPeriodOverview().period_shortname;
        this._loadPeriod();
    },

    _loadPeriod: function() {
        var store = this.getPeriodsStore();
        store.loadPeriod(
            this.period_shortname, this._onLoadPeriod, this
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
        // TODO
    },

    _onLoadPeriodSuccess: function(record) {
        this.assignmentRecord = record;
        //this.application.fireEvent('periodSuccessfullyLoaded', record);
        this.getActions().setTitle(record.get('long_name'));
    },
});
