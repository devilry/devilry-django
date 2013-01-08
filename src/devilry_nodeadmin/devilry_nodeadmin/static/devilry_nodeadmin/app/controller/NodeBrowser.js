Ext.define('devilry_nodeadmin.controller.NodeBrowser', {
    extend: 'Ext.app.Controller',

    views: [
        'defaultNodeList',
        'nodeChildrenList',
        'nodeDetailsOverview'
    ],

    stores: [
        'NodeChildren',
        'NodeDetails',
        'RelatedNodes'
    ],

    models: [
        'Details',
        'Node',
        'Parent',
        'Subject'
    ],

    refs: [
        {
            ref: 'viewport primary',
            selector: ''
        },
        {
            ref: 'viewport secondary',
            selector: ''
        }
    ],

    init: function() {

        /*
        this.control({
            'viewport dashboard ': {
                render: this._onRenderAllWhereIsAdminList
            }
        });
        this.mon(this.getAllActivesWhereIsAdminStore().proxy, {
            scope: this,
            exception: this._onProxyError
        });
        */
    },

    /*
    _onRenderAllWhereIsAdminList: function() {
        this.getAllActivesWhereIsAdminStore().load({
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadSuccess(records);
                } else {
                    // NOTE: Errors are handled in _onProxyError
                }
            }
        });
    }
    */
});

