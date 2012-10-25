/**
 * Approved previous period wizard
 */
Ext.define('devilry_subjectadmin.controller.ApprovedPreviousPeriod', {
    extend: 'Ext.app.Controller',
    mixins: [
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    requires: [
    ],

    views: [
        'approvedpreviousperiod.Overview'
    ],

    models: [
    ],
    stores: [
        'Assignments'
    ],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: '#appAlertmessagelist'
    }, {
        ref: 'overview',
        selector: 'approvedpreviousperiodoverview',

    // Select assignments page
    }, {
        ref: 'nextButton',
        selector: 'approvedpreviousperiodoverview #nextButton'
    }],

    init: function() {
        this.control({
            'approvedpreviousperiodoverview': {
                render: this._onRender
            },
            'approvedpreviousperiodoverview selectassignmentsgrid': {
                selectionchange: this._onAssignmentSelectionChange
            }
        });
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        var period_id = this.getOverview().period_id;
        this._loadAssignments(period_id);
    },

    //_onProxyError: function(response, operation) {
        //if(this.getOverview() && this.getOverview().isVisible()) { // NOTE: Some of the proxies are used in many views. We only want to handle them if we are in the AddGroups view
            //this.getOverview().setLoading(false);
            //this.handleProxyErrorNoForm(this.application.getAlertmessagelist(), response, operation);
        //}
    //},
    //_onAssignmentProxyError: function(proxy, response, operation) {
        //this._onProxyError(response, operation);
    //},


    //
    //
    // Load stores
    //
    //
    _loadAssignments: function(period_id) {
        this.getAssignmentsStore().loadAssignmentsInPeriod(period_id, this._onLoadAssignments, this);
    },

    _onLoadAssignments: function(records, operation) {
        if(operation.success) {
        } else {
            this.onLoadFailure(operation);
        }
    },


    //
    //
    // select assignments page
    //
    //
    _onAssignmentSelectionChange: function(selModel, selected) {
        if(selected.length === 0) {
            this.getNextButton().disable();
        } else {
            this.getNextButton().enable();
        }
    }
});
