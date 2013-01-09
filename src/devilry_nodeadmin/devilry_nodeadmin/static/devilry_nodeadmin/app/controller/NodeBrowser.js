Ext.define('devilry_nodeadmin.controller.NodeBrowser', {
    extend: 'Ext.app.Controller',

    views: [
        'nodeChildrenList',
        'nodeDetailsOverview',
        'nodeParentLink'
    ],

    stores: [
        'NodeChildren',
        'NodeDetails'
    ],

    models: [
        'Details',
        'Node'
    ],

    refs: [],

    init: function() {



    }

});

