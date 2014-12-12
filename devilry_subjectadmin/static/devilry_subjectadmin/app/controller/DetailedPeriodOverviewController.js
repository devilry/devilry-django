Ext.define('devilry_subjectadmin.controller.DetailedPeriodOverviewController', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'detailedperiodoverview.DetailedPeriodOverview'
    ],

    stores: ['AggregatedRelatedStudentInfos'],
    models: [
        'Period',
        'DetailedPeriodOverview'
    ],

    refs: [{
        ref: 'overview',
        selector: 'viewport detailedperiodoverview'
    }, {
        ref: 'header',
        selector: 'viewport detailedperiodoverview #header'
    }, {
        ref: 'detailsGrid',
        selector: 'viewport detailedperiodoverview detailedperiodoverviewgrid'
    }],

    init: function() {
        this.control({
            'viewport detailedperiodoverview': {
                render: this._onRender
            }
        });

        this.mon(this.getDetailedPeriodOverviewModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
    },

    _onRender: function() {
        this.period_id = this.getOverview().period_id;
        this.loadPeriod();
    },

    //
    //
    // Load period
    //
    //

    loadPeriod: function() {
        this.setLoadingBreadcrumb();
        this.getPeriodModel().load(this.period_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this._onLoadPeriodSuccess(record);
                } else {
                    // NOTE: Errors is handled in onPeriodProxyError
                }
            }
        });
    },
    _onLoadPeriodSuccess: function(record) {
        this.periodRecord = record;
        this._loadDetailedPeriodOverview();
    },

    //
    //
    // Load detailed period overview
    //
    //
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
        this._onAllLoaded();
    },
    _onProxyError: function(proxy, response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
    },


    //
    //
    // Create grid
    //
    //

    _onAllLoaded:function () {
        var path = this.getPathFromBreadcrumb(this.periodRecord);
        var label = gettext('Detailed overview');
        this.getHeader().update({
            loading: false,
            periodpath: path
        });
        this.application.setTitle(Ext.String.format('{0} - {1}', label, path));
        this.setSubviewBreadcrumb(this.periodRecord, 'Period', [], label);
        this._setupGrid();
    },

    _setupGrid: function () {
        var grid = this.getDetailsGrid();
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
    }
});
