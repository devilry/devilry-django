Ext.define('devilry_subjectadmin.controller.Dashboard', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'dashboard.Dashboard'
    ],

    stores: [
        'AllActivesWhereIsAdmin'
    ],

    refs: [{
        ref: 'allWhereIsAdminList',
        selector: 'allactivewhereisadminlist'
    }],

    init: function() {
        this.control({
            'viewport dashboard allactivewhereisadminlist': {
                render: this._onRenderAllWhereIsAdminList
            }
        });
        this.mon(this.getAllActivesWhereIsAdminStore().proxy, {
            scope: this,
            exception: this._onProxyError
        });
    },

    _onRenderAllWhereIsAdminList: function() {
        this.getAllActivesWhereIsAdminStore().load({
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadSuccess(records);
                } else {
                    // NOTE: Errors are handled in _onProxyError
                }
            }
        });
    },

    _onLoadSuccess: function(records) {
        this.getAllWhereIsAdminList().update({
            loadingtext: null,
            subjects: records
        });
    },

    _onProxyError: function(proxy, response, operation) {
        this.handleProxyErrorNoForm(this.application.getAlertmessagelist(),
            response, operation);
    },
});

