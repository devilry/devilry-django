Ext.define('devilry_nodeadmin.controller.NodeBrowser', {
    extend: 'Ext.app.Controller',

    views: [
        'defaultNodeList',
        'nodeChildrenList',
        'nodeDetailsOverview',
        'nodeParentLink',
    ],

    stores: [
        'NodeChildren',
        'NodeDetails',
    ],

    models: [
        'Details',
        'Node',
    ],

    refs: [
        {
            ref: 'primary',
            selector: 'viewport primary'
        },
        {
            ref: 'viewport secondary',
            selector: ''
        }
    ],

    init: function() {



    }

});

