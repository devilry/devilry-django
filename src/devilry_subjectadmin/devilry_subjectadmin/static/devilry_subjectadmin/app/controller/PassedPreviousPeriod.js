/**
 * Passed previous period wizard
 */
Ext.define('devilry_subjectadmin.controller.PassedPreviousPeriod', {
    extend: 'Ext.app.Controller',
    mixins: [
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin',
        'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin'
    ],

    requires: [
    ],

    views: [
        'passedpreviousperiod.Overview'
    ],

    models: ['Assignment'],
    stores: ['PassedPreviousPeriodItems'],

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
        this.getOverview().setLoading(true);
        this.assignment_id = this.getOverview().assignment_id;
        this.loadAssignment(this.assignment_id);
    },

    _onAssignmentProxyError: function(proxy, response, operation) {
        this._onProxyError(response, operation);
    },
    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;

        var text = interpolate(gettext('Passed in previous %(period_term)s'), {
            period_term: gettext('period')
        }, true);
        this.setSubviewBreadcrumb(this.assignmentRecord, 'Assignment', [], text);
        var path = this.getPathFromBreadcrumb(this.assignmentRecord);
        this.application.setTitle(Ext.String.format('{0}.{1}', path, text));

        this._loadStore(this.assignment_id);
    },
    onLoadAssignmentFailure: function(operation) {
        this.getOverview().setLoading(false);
        this.onLoadFailure(operation);
    },


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
        this.getOverview().setLoading(false);
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
