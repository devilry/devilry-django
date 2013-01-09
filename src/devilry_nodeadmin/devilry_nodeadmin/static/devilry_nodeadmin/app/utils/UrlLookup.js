Ext.define('devilry_nodeadmin.utils.UrlLookup', {
    singleton: true,

    nodeChildren: function( node_pk ) {
        return Ext.String.format('#/rest/{0}/children', node_pk );
    }

});
