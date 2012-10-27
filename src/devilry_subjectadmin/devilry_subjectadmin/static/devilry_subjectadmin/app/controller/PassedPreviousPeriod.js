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
    }, {
        ref: 'cardContainer',
        selector: 'passedpreviousperiodoverview #cardContainer',

    // Select groups page
    }, {
        ref: 'groupsGrid',
        selector: 'passedpreviousperiodoverview #pageOne selectpassedpreviousgroupsgrid'
    }, {
        ref: 'nextButton',
        selector: 'passedpreviousperiodoverview #pageOne #nextButton'
    }],

    init: function() {
        this.control({
            'passedpreviousperiodoverview': {
                render: this._onRender
            },
            'passedpreviousperiodoverview #pageOne selectpassedpreviousgroupsgrid': {
                selectionchange: this._onGroupsSelectionChange
            },
            'passedpreviousperiodoverview #pageOne #nextButton': {
                click: this._onNextButton
            }
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
            this.getGroupsGrid().selectWithPassingGradeInPrevious();
        } else {
            this.onLoadFailure(operation);
        }
    },


    //
    //
    // Page 1
    //
    //
    _onGroupsSelectionChange: function(selModel, selected) {
        if(selected.length === 0) {
            this.getNextButton().disable();
        } else {
            this.getNextButton().enable();
        }
    },

    _onNextButton: function() {
        this.getCardContainer().getLayout().setActiveItem('pageTwo');
    },

    //
    //
    // Page 2
    //
    //
    _onBackButton: function() {
        this.getCardContainer().getLayout().setActiveItem('pageOne');
    },
});
