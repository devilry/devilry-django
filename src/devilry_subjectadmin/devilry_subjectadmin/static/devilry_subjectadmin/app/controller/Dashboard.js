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
        selector: 'allwhereisadminlist'
    }],

    init: function() {
        this.control({
            // Listen for events by selector
            'viewport dashboard allwhereisadminlist': {
                // NOTE: Important that we listen for #listOfSubjects, and not
                // for the panel, since the panel is rendered before the list,
                // which would mess up our code that requires the list to be
                // rendered.
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

