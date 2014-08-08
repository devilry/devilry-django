Ext.define('devilry_qualifiesforexam.controller.PeriodControllerMixin', {
    extend: 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',

    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_subjectadmin.model.Period'
    ],

    loadPeriod: function(period_id) {
        devilry_subjectadmin.model.Period.load(period_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this._onLoadPeriodSuccess(record);
                } else {
                    this._onLoadPeriodFailure(operation);
                }
            }
        });
    },

    _onPeriodFailure: function(operation) {
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler', operation);
        error.addErrors(null, operation);
        this.application.getAlertmessagelist().addMany(error.errormessages, 'error', true);
    },

    _onLoadPeriodSuccess: function (record) {
        this.periodRecord = record;
        var args = [this.periodRecord, 'Period'];
        args = args.concat(this.getAppBreadcrumbs());
        Ext.bind(this.setSubviewBreadcrumb, this, args)();
        this.onLoadPeriodSuccess();
    },

    getAppBreadcrumbs: function () {
        return [[], 'Undefined'];
    },

    onLoadPeriodSuccess: function () {
    }
});