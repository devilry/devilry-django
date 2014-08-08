Ext.define('devilry_nodeadmin.utils.UrlLookup', {
    singleton: true,

    qualifiedForExamsSummary: function(node_id) {
        return Ext.String.format('{0}/devilry_qualifiesforexam/#/summary/{1}',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX, node_id);
    },

    nodeChildren: function( node_id ) {
        return Ext.String.format('#/rest/{0}/children', node_id );
    },

    aggregatedstudentinfo: function(user_id) {
        return Ext.String.format('/aggregatedstudentinfo/{0}', user_id);
    }
});
