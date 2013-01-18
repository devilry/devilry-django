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

    stores: [
        'NodeChildren',
        'NodeDetails'
    ],

    models: [
        'Details',
        'Node'
    ],

    refs: [{
        ref: 'overview',
        selector: 'nodebrowseroverview'
    }, {
        ref: 'primary',
        selector: 'nodebrowseroverview #primary'
    }, {
        ref: 'secondary',
        selector: 'nodebrowseroverview #secondary'
    }],

    init: function() {
        this.control({
            'viewport nodebrowseroverview #primary': {
                render: this._onRenderPrimary
            }
        });
    },

    _onRenderPrimary: function() {
        var node_pk = this.getOverview().node_pk;

        // STORES
        // children
        this.getNodeChildrenStore().collectByNode( node_pk, {
            scope: this,
            callback: function ( records, op ) {
                if( op.success ) {
                    this._onLoadNodeChildrenSuccess( records );
                } else {
                    this._onLoadError(op);
                }
            }
        });

        // details
        this.getNodeDetailsStore().collectByNode( node_pk, {
            scope: this,
            callback: function ( records, op ) {
                if( op.success ) {
                    this._onLoadNodeDetailsSuccess( records );
                } else {
                    this._onLoadError( op );
                }
            }
        });

        this.getPrimary().add([{
            xtype: 'navigator',
            node_pk: node_pk
        }, {
            xtype: 'nodechildrenlist',
            node_pk: node_pk
        }]);


        this.getSecondary().add([{
            xtype: 'nodedetailsoverview',
            node_pk: node_pk
        }]);

    },

    _onRenderSecondary: function() {},

    _onLoadNodeDetailsSuccess:function ( records ) {
        // convert to the breadcrumb object format
        var current = records[0].data;
        var path = current.path;

        var breadcrumb = [];

        Ext.Array.each( path, function(element) {
            breadcrumb.push( {
                text: element.short_name,
                url: Ext.String.format( "/devilry_nodeadmin/#/node/{0}", element.id )
            } )
        } );

        this.application.breadcrumbs.set( breadcrumb, gettext( 'Om noden' ) );
    },

    _onLoadNodeChildrenSuccess:function ( records ) {},

    _onLoadError:function (op) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrorsFromOperation(op);
        this.application.getAlertmessagelist().addMany(
            errorhandler.errormessages, 'error', true );
    }
});

