Ext.define('devilry_nodeadmin.controller.NodeBrowserController', {
    extend: 'Ext.app.Controller',

    views: [
        'nodebrowser.NodeBrowserOverview'
    ],

    requires: [
        'devilry_nodeadmin.view.nodebrowser.NodeChildrenList',
        'devilry_nodeadmin.view.nodebrowser.NodeDetailsOverview',
        'devilry_nodeadmin.view.nodebrowser.Navigator',

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
    }, {
        ref: 'navigator',
        selector: 'navigator'
    }, {
        ref: 'nodeChildrenList',
        selector: 'nodechildrenlist'
    }],

    init: function() {
        this.control({
            'viewport nodebrowseroverview navigator': {
                render: this._onRenderDetailContainer
            },
            'viewport nodebrowseroverview nodechildrenlist': {
                render: this._onRenderDetailContainer
            },
            'viewport nodebrowseroverview nodedetailsoverview': {
                render: this._onRenderDetailContainer
            }
        });
    },

    _onRenderDetailContainer: function() {
        this.getOverview().setLoading(true);

        // Make sure all the views using the details data have been rendered
        if(this.getNodeDetailsOverview().rendered && this.getNavigator().rendered && this.getNodeChildrenList().rendered) {
            this._loadNodeDetails();
        }
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
        var breadcrumb = [];
        for (var i = 0; i < path.length-1; i++) {
            var element = path[i];
            breadcrumb.push({
                text: element.short_name,
                url: Ext.String.format("{0}/devilry_nodeadmin/#/node/{1}",
                    window.DevilrySettings.DEVILRY_URLPATH_PREFIX, element.id)
            });
        }
        this.application.breadcrumbs.set( breadcrumb, path[path.length-1].short_name);
        this.getNodeDetailsOverview().update(record.data);
        this.getNavigator().update({
            predecessor: path.length == 1? null: path[path.length-2]
        });
        this.getNodeChildrenList().update({
            nodes: record.get('childnodes')
        });
    },

    _onLoadError:function (op) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrorsFromOperation(op);
        this.application.getAlertmessagelist().addMany(
            errorhandler.errormessages, 'error', true );
    }
});
