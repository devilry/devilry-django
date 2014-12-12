Ext.define('devilry_nodeadmin.controller.DashboardController', {
    extend: 'Ext.app.Controller',

    views: [
        'dashboard.DashboardOverview',
        'dashboard.BetaWarning',
        'dashboard.ToplevelNodeList'
    ],
    requires: [
        'devilry_nodeadmin.utils.UrlLookup'
    ],

    stores: [
        'ToplevelNodes'
    ],

    refs: [{
        ref: 'overview',
        selector: 'dashboardoverview'
    }, {
        ref: 'userSearchBox',
        selector: 'dashboardoverview autocompleteuserwidget#userSearchBox'
    }],

    init: function() {
        this.control({
            'viewport dashboardoverview toplevelnodelist': {
                render: this._onRender
            },
            'viewport dashboardoverview autocompleteuserwidget#userSearchBox': {
                userSelected: this._onUserSelected
            }
        });
    },

    _onRender: function() {
        this.getToplevelNodesStore().load({
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadRelatedNodesSuccess(records);
                } else {
                    this._onLoadError(op);
                }
            }
        });

    },

    _onLoadRelatedNodesSuccess: function(records) {
    },

    _onLoadError:function (op) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrorsFromOperation(op);
        this.application.getAlertmessagelist().addMany(
            errorhandler.errormessages, 'error', true );
    },

    _onUserSelected: function(combo, userRecord) {
        this.getUserSearchBox().clearValue();
        this.application.route.navigate(devilry_nodeadmin.utils.UrlLookup.aggregatedstudentinfo(userRecord.get('id')));
    }
});

