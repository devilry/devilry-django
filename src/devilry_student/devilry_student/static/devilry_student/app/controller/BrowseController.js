Ext.define('devilry_student.controller.BrowseController', {
    extend: 'Ext.app.Controller',

    views: [
        'browse.Browse',
        'browse.BrowseList',
        'browse.BrowseCalendar'
    ],

    stores: [
        'GroupedResults'
    ],

    refs: [{
        ref: 'browse',
        selector: 'viewport browse browselist'
    }],

    init: function() {
        this.control({
            'viewport browse browselist': {
                render: this._onRenderList
            }
        });
    },

    _onRenderList: function() {
        this.getGroupedResultsStore().load({
            scope: this,
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
