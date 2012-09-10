Ext.define('devilry_subjectadmin.controller.Dashboard', {
    extend: 'Ext.app.Controller',

    views: [
        'dashboard.Dashboard'
    ],

    stores: [
        'AllActivesWhereIsAdmin'
    ],

    refs: [{
        // Create selector method for the ``allwhereisadminpanel`` widget called getAllWhereIsAdminPanel()
        ref: 'allWhereIsAdminList',
        selector: 'allactivewhereisadminlist'
    }],

    init: function() {
        this.control({
            'viewport dashboard allactivewhereisadminlist': {
                render: this._onRenderAllWhereIsAdminList
            }
        });
    },

    _onRenderAllWhereIsAdminList: function() {
        this.getAllActivesWhereIsAdminStore().load({
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadSuccess(records);
                } else {
                    this._onLoadError(op);
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

    _onLoadError: function(op) {
        console.log('load error', op);
    }
});

