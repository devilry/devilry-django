Ext.define('devilry_qualifiesforexam.controller.QualifiesForExamSelectPluginController', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_qualifiesforexam.controller.PeriodControllerMixin'
    ],

    views: [
        'selectplugin.QualifiesForExamSelectPlugin'
    ],

    stores: [
        'Plugins'
    ],

    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.HtmlErrorDialog'
    ],


    refs: [{
        ref: 'overview',
        selector: 'selectplugin'
    }],

    init: function() {
        this.control({
            'viewport selectplugin': {
                render: this._onRender
            }
        });
        this.mon(this.getPluginsStore().proxy, {
            scope: this,
            exception: this._onProxyError
        });
    },

    _onRender: function() {
        this.periodid = this.getOverview().periodid;
        this.getPluginsStore().load({
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadSuccess(records);
                }
                // NOTE: Errors are handled in _onProxyError
            }
        });
    },

    _onLoadSuccess: function(records) {
        this.loadPeriod(this.periodid);
    },

    getAppBreadcrumbs: function () {
        var text = gettext('Qualified for final exams') + ' - ' + gettext('how?');
        return [[], text];
    },

    _onProxyError: function(proxy, response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
    }
});

