Ext.define('devilry_qualifiesforexam_select.controller.SelectQualifiedStudentsGridController', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'SelectQualifiedStudentsGrid'
    ],

    stores: ['AggregatedRelatedStudentInfos'],
    models: [
        'DetailedPeriodOverview'
    ],

    refs: [{
        ref: 'header',
        selector: 'viewport #header'
    }, {
        ref: 'grid',
        selector: 'viewport selectqualifiedstudentsgrid'
    }],

    init: function() {
        this.control({
            'viewport selectqualifiedstudentsgrid': {
                render: this._onRender
            },
            'viewport selectqualifiedstudentsgrid #backButton': {
                click: this._onBackButtonClick
            },
            'viewport selectqualifiedstudentsgrid #nextButton': {
                click: this._onNextButtonClick
            }
        });

        this.mon(this.getDetailedPeriodOverviewModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
    },

    _onRender: function() {
        var query = Ext.Object.fromQueryString(window.location.search);
        this.backurl = window.devilry_qualifiesforexam_select_opts.backurl;
        this.period_id = query.periodid;
        this.getGrid().setLoading();
        this._loadDetailedPeriodOverview();
    },


    _loadDetailedPeriodOverview: function() {
        this.getDetailedPeriodOverviewModel().load(this.period_id, {
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadDetailedPeriodOverviewSuccess(records);
                }
                // NOTE: Errors are handled in _onProxyError
            }
        });
    },
    _onLoadDetailedPeriodOverviewSuccess: function(record) {
        this.detailedPeriodOverviewRecord = record;
        this.getGrid().setLoading();
        this._onAllLoaded();
    },
    _onProxyError: function(proxy, response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
    },


    _onAllLoaded:function () {
        var grid = this.getGrid();
        var assignments = this.detailedPeriodOverviewRecord.get('assignments');
        grid.addColumnForEachAssignment(assignments);
        grid.addAssignmentSorters(assignments);
        this.getAggregatedRelatedStudentInfosStore().loadData(
            this.detailedPeriodOverviewRecord.get('relatedstudents'));

        var ignored_with_feedback = this.detailedPeriodOverviewRecord.get(
            'students_with_feedback_that_is_candidate_but_not_in_related');
        var ignored_without_feedback = this.detailedPeriodOverviewRecord.get(
            'students_with_no_feedback_that_is_candidate_but_not_in_related');
        grid.handleIgnored(this.period_id, ignored_with_feedback, ignored_without_feedback);
        grid.sortByFullname();

        this.getGrid().setLoading(false);
    },

    _onBackButtonClick: function() {
        window.location.href = this.backurl;
    },

    _onNextButtonClick: function() {
        
    }
});

