/**
 * Passed previous period wizard
 */
Ext.define('devilry_subjectadmin.controller.PassedPreviousPeriod', {
    extend: 'Ext.app.Controller',
    mixins: [
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    requires: [
    ],

    views: [
        'passedpreviousperiod.Overview'
    ],

    stores: [
        'PassedPreviousPeriodItems'
    ],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: '#appAlertmessagelist'
    }, {
        ref: 'overview',
        selector: 'passedpreviousperiodoverview',

    //// Select assignments page
    //}, {
        //ref: 'nextButton',
        //selector: 'passedpreviousperiodoverview #nextButton'
    }],

    init: function() {
        this.control({
            'passedpreviousperiodoverview': {
                render: this._onRender
            },
            //'passedpreviousperiodoverview selectassignmentsgrid': {
                //selectionchange: this._onAssignmentSelectionChange
            //}
        });
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        var assignment_id = this.getOverview().assignment_id;
        this._loadStore(assignment_id);
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
    // Load store
    //
    //
    _loadStore: function(assignment_id) {
        this.getPassedPreviousPeriodItemsStore().loadGroupsInAssignment(assignment_id, {
            scope: this,
            callback: this._onLoadStore
        });
    },

    _onLoadStore: function(records, operation) {
        if(operation.success) {
            console.log('success', records);
        } else {
            this.onLoadFailure(operation);
        }
    },


    //
    //
    // select assignments page
    //
    //
    //_onAssignmentSelectionChange: function(selModel, selected) {
        //if(selected.length === 0) {
            //this.getNextButton().disable();
        //} else {
            //this.getNextButton().enable();
        //}
    //}
});
