Ext.define('devilry_qualifiesforexam.controller.SummaryViewController', {
    extend: 'Ext.app.Controller',

    views: [
        'summaryview.SummaryView'
    ],

    stores: [
        'Statuses'
    ],

    refs: [{
        ref: 'summaryView',
        selector: 'summaryview'
    }],

    init: function() {
        this.control({
            'viewport summaryview summaryviewgrid': {
                render: this._onRender
            }
        });
        this.mon(this.getStatusesStore().proxy, {
            scope: this,
            exception: this._onProxyError
        });
    },

    _onRender: function() {
        this.getSummaryView().setLoading();
        this.nodeid = this.getSummaryView().periodid;
        this.application.setTitle(gettext('Summary - Qualifies for exam'));
        this.getStatusesStore().load({
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadSuccess(records);
                } // NOTE: Errors are handled in _onProxyError
            }
        });
    },

    _onLoadSuccess: function(records) {
        this.getSummaryView().setLoading(false);
    },


    _onProxyError: function(proxy, response, operation) {
        if(!Ext.isEmpty(this.getSummaryView()) && this.getSummaryView().isVisible()) {
            this.getSummaryView().setLoading(false);
            var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
            errorhandler.addErrors(response, operation);
            this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
        }
    }
});
