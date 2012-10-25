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
        selector: 'approvedpreviousperiodoverview'
    }],

    init: function() {
        this.control({
            'approvedpreviousperiodoverview': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        var period_id = this.getOverview().period_id;
        this._loadAssignments(this.period_id);
    },

    _onProxyError: function(response, operation) {
        if(this.getOverview() && this.getOverview().isVisible()) { // NOTE: Some of the proxies are used in many views. We only want to handle them if we are in the AddGroups view
            this.getOverview().setLoading(false);
            this.handleProxyErrorNoForm(this.application.getAlertmessagelist(), response, operation);
        }
    },
    _onAssignmentProxyError: function(proxy, response, operation) {
        this._onProxyError(response, operation);
    },


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
            console.log(records);
        } else {
            this.onLoadFailure(operation);
        }
    }
});
