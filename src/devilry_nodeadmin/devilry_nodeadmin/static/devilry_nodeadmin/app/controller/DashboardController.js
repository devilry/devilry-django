Ext.define('devilry_nodeadmin.controller.DashboardController', {
    extend: 'Ext.app.Controller',

    views: [
        'dashboard.DashboardOverview'
    ],

    stores: [
        'RelatedNodes'
    ],

    models: [
        'Node'
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
        });
    },

    _onRenderSecondary: function() {

        // STORES

        // related nodes
        this.getRelatedNodesStore().collect( {
            scope: this,
            callback: function( records, op ) {
                if( op.success ) {
                    this._onLoadRelatedNodesSuccess( records );
                } else {
                    this._onLoadError(op);
                }
            }
        });

    },

    _onLoadRelatedNodes: function( records ) {},

    _onLoadError:function (op) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrorsFromOperation(op);
        this.application.getAlertmessagelist().addMany(
            errorhandler.errormessages, 'error', true );
    }

});

