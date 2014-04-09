Ext.define('devilry_qualifiesforexam_select.controller.SelectQualifiedStudentsController', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'SelectQualifiedStudentsView'
    ],

    requires: [
        'Ext.form.action.StandardSubmit'
    ],

    stores: ['AggregatedRelatedStudentInfos'],
    models: [
        'DetailedPeriodOverview'
    ],

    refs: [{
        ref: 'header',
        selector: 'viewport selectqualifiedstudentsview #header'
    }, {
        ref: 'form',
        selector: 'viewport selectqualifiedstudentsview'
    }, {
        ref: 'grid',
        selector: 'viewport selectqualifiedstudentsgrid'
    }],

    init: function() {
        this.control({
            'viewport selectqualifiedstudentsgrid': {
                render: this._onRender
            },
            'viewport selectqualifiedstudentsview #backButton': {
                click: this._onBackButtonClick
            },
            'viewport selectqualifiedstudentsview #nextButton': {
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
            callback: function(record, op) {
                if(op.success) {
                    this._onLoadDetailedPeriodOverviewSuccess(record);
                }
                // NOTE: Errors are handled in _onProxyError
            }
        });
    },
    _onLoadDetailedPeriodOverviewSuccess: function(record) {
        this.detailedPeriodOverviewRecord = record;
        this.getGrid().setLoading();
        // NOTE: Without this, some browsers (IE and Chrome) seems to flash the correct dataset in the
        // grid, and then render an empty grid. No idea why this happens, but
        // a short delay seems to solve the problem.
        Ext.defer(function() {
            this._onAllLoaded();
        }, 400, this);
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
        var selected = this.getGrid().getSelectionModel().getSelection();
        var qualified_relstudentids = [];
        for(var index=0; index<selected.length; index++)  {
            var item = selected[index];
            qualified_relstudentids.push(item.get('relatedstudent').id);
        }
        this.getForm().submit({
            url: window.location.href,
            method: 'POST',
            standardSubmit: true,
            params: {
                qualified_relstudentids: qualified_relstudentids
            }
        });
    }
});

