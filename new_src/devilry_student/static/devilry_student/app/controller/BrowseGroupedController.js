Ext.define('devilry_student.controller.BrowseGroupedController', {
    extend: 'Ext.app.Controller',

    views: [
        'browsegrouped.BrowseGrouped'
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
        var title = gettext('History');
        if(activeonly) {
            title = Ext.create('Ext.XTemplate', gettext('Active {period_term}')).apply({
                period_term: gettext('period')
            });
        }
        this.application.breadcrumbs.set([], title);
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
