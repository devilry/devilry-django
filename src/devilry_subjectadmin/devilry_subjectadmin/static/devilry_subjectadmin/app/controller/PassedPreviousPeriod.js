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
        console.log(record.data);

        var text = gettext('Passed previously');
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
            var selModel = this.getGroupsGrid().getSelectionModel();
            selModel.select(0, true);
            selModel.select(1, true);
            Ext.defer(function() {
                this._onNextButton();
            }, 300, this);
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
        var store = this.getPassedPreviousPeriodItemsStore();
        var selModel = this.getGroupsGrid().getSelectionModel();
        store.filterBy(function(record) {
            return selModel.isSelected(record);
        });
        store.each(function(record) {
            var oldgroup = record.get('oldgroup');
            if(Ext.isEmpty(oldgroup)) {
                
            } else {
                record.set('comment', Ext.String.format('Devilry autodetected that you passed this assignment {0}.',
                    oldgroup.period.long_name));
                record.set('grade', oldgroup.feedback.grade);
            }
        });
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
