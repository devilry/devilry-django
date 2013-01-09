Ext.define('devilry_subjectadmin.controller.DetailedPeriodOverviewController', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'detailedperiodoverview.DetailedPeriodOverview'
    ],

//    stores: ['RelatedStudents'],
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
    }],

    init: function() {
        this.control({
            'viewport detailedperiodoverview': {
                render: this._onRender
            }
        });

//        this.mon(this.getRelatedStudentsStore().proxy, {
//            scope: this,
//            exception: this.onRelatedStoreProxyError
//        });
    },

    _onRender: function() {
        var period_id = this.getOverview().period_id;
        this.loadPeriod(period_id);
    },

    //
    //
    // Load period
    //
    //

    loadPeriod: function(period_id) {
        this.setLoadingBreadcrumb();
        this.getPeriodModel().load(period_id, {
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

    _onAllLoaded:function () {
        var path = this.getPathFromBreadcrumb(this.periodRecord);
        var label = gettext('Detailed overview');
        this.getHeader().update({
            loading: false,
            periodpath: path
        });
        this.application.setTitle(Ext.String.format('{0} - {1}', label, path));
        this.setSubviewBreadcrumb(this.periodRecord, 'Period', [], label);
    }
});
