Ext.define('devilry_nodeadmin.controller.NodeBrowserController', {
    extend: 'Ext.app.Controller',

    views: [
        'nodebrowser.NodeBrowserOverview'
    ],

    requires: [
        'devilry_nodeadmin.view.nodebrowser.NodeDetailsOverview',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.DatetimeHelpers'
    ],

    models: [
        'NodeDetail'
    ],

    refs: [{
        ref: 'overview',
        selector: 'nodebrowseroverview'
    }, {
        ref: 'nodeDetailsOverview',
        selector: 'nodedetailsoverview'
    }],

    init: function() {
        this.control({
            'viewport nodebrowseroverview nodedetailsoverview': {
                render: this._onRenderDetailContainer
            }
        });
    },

    _onRenderDetailContainer: function() {
        this.getOverview().setLoading(true);
        this._loadNodeDetails();
    },

    _loadNodeDetails: function() {
        this.getNodeDetailModel().load(this.getOverview().node_pk, {
            scope: this,
            callback: function ( records, op ) {
                this.getOverview().setLoading(false);
                if( op.success ) {
                    this._onLoadNodeDetailsSuccess( records );
                } else {
                    this._onLoadError( op );
                }
            }
        });
    },

    _onLoadNodeDetailsSuccess:function ( record ) {
        var path = record.get('path');
        var breadcrumb = [{
            text: gettext('Administrator'),
            url: ''
        }];
        for (var i = 0; i < path.length-1; i++) {
            var element = path[i];
            breadcrumb.push({
                text: element.short_name,
                url: Ext.String.format("{0}/devilry_nodeadmin/#/node/{1}",
                    window.DevilrySettings.DEVILRY_URLPATH_PREFIX, element.id)
            });
        }
        this.application.breadcrumbs.set( breadcrumb, path[path.length-1].short_name);
        this.getNodeDetailsOverview().update({
            node: record.data,
            childnodes: record.get('childnodes'),
            noChildren: record.get('subjects').length == 0 && record.get('childnodes').length == 0
        });
    },

    _onLoadError:function (op) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrorsFromOperation(op);
        this.application.getAlertmessagelist().addMany(
            errorhandler.errormessages, 'error', true );
    }
});
