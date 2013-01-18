Ext.define('devilry_nodeadmin.controller.DashboardController', {
    extend: 'Ext.app.Controller',

    views: [
        'dashboard.DashboardOverview',
        'dashboard.BetaWarning'
    ],

    stores: [
        'RelatedNodes'
    ],

    models: [
        'Node'
    ],

    refs: [{
        ref: 'overview',
        selector: 'dashboardoverview'
    }, {
        ref: 'primary',
        selector: 'dashboardoverview #primary'
    }, {
        ref: 'secondary',
        selector: 'dashboardoverview #secondary'
    }],

    init: function() {
        this.control({
            'viewport dashboardoverview #primary': {
                render: this._onRenderPrimary
            },
            'viewport dashboardoverview #secondary': {
                render: this._onRenderSecondary
            }
        });
    },

    _onRenderPrimary: function() {

        // STORES
        // related nodes
        this.getRelatedNodesStore().collectAll( {
            scope: this,
            callback: function( records, op ) {
                if( op.success ) {
                    this._onLoadRelatedNodesSuccess( records );
                } else {
                    this._onLoadError( op );
                }
            }
        });

        this.getPrimary().add([
            { xtype: 'defaultnodelist' }
        ]);
    },

    _onRenderSecondary: function() {

        this.getSecondary().add([
            { xtype: 'betawarning' }
        ]);

    },



    _onLoadRelatedNodesSuccess: function( records ) {},

    _onLoadError:function (op) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrorsFromOperation(op);
        this.application.getAlertmessagelist().addMany(
            errorhandler.errormessages, 'error', true );
    }

});

