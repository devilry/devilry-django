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
        var label = gettext('All my courses');
        this.application.breadcrumbs.set([{
            text: gettext('Course manager'),
            url: '#'
        }], label);
    },

    _onLoadSuccess: function(records) {
        this.getAllWhereIsAdminList().update({
            loadingtext: null,
            subjects: records
        });
    }
});
