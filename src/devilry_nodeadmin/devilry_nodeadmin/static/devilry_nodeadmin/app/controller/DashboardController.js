Ext.define('devilry_nodeadmin.controller.DashboardController', {
    extend: 'Ext.app.Controller',

    views: [
        'dashboard.DashboardOverview'
    ],

    stores: [
        'RelatedNodes'
    ],

    refs: [{
        ref: 'secondary',
        selector: 'dashboardoverview #secondary'
    }],

    init: function() {
        this.control({
            'viewport dashboardoverview #secondary': {
                render: this._onRenderSecondary
            }
        })
    },

    _onRenderSecondary: function() {
//        this.getSecondary().update('Hei')
    }
});

