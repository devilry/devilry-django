Ext.define('devilry_subjectadmin.controller.AllWhereIsAdmin', {
    extend: 'Ext.app.Controller',

    views: [
        'allwhereisadmin.AllWhereIsAdminPanel'
    ],

    stores: [
        'AllWhereIsAdmin'
    ],

    refs: [{
        ref: 'allWhereIsAdminList',
        selector: 'allwhereisadminlist'
    }],

    init: function() {
        this.control({
            'viewport allwhereisadminpanel allwhereisadminlist': {
                render: this._onRenderAllWhereIsAdminList
            }
        });
    },

    _onRenderAllWhereIsAdminList: function() {
        this.getAllWhereIsAdminStore().load({
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadSuccess(records);
                } else {
                    // NOTE: Errors are handled in _onProxyError
                }
            }
        });
        var label = interpolate(gettext('All my %(subjects_term)s'), {
            subjects_term: gettext('subjects')
        }, true);
        this.application.breadcrumbs.set([], label);
    },

    _onLoadSuccess: function(records) {
        this.getAllWhereIsAdminList().update({
            loadingtext: null,
            subjects: records
        });
    }
});
