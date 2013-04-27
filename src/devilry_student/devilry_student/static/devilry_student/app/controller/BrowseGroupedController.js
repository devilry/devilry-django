Ext.define('devilry_student.controller.BrowseGroupedController', {
    extend: 'Ext.app.Controller',

    views: [
        'browse.BrowseGrouped'
    ],

    stores: [
        'GroupedResults'
    ],

    refs: [{
        ref: 'browseGrouped',
        selector: 'viewport browsegrouped'
    }],

    init: function() {
        this.control({
            'viewport browsegrouped': {
                render: this._onRenderList
            }
        });
    },

    _onRenderList: function() {
        var activeonly = this.getBrowseGrouped().activeonly;
        console.log(activeonly);
        this.getGroupedResultsStore().load({
            scope: this,
            params: {
                activeonly: activeonly? 'true': ''
            },
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadResultsSuccess();
                }
            }
        });
    },

    _onLoadResultsSuccess: function() {
        
    }
});
