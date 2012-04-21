Ext.define('devilry.extjshelpers.assignmentgroup.FileMetaBrowserWindow', {
    extend: 'Ext.window.Window',
    title: 'Files',
    height: 400,
    width: 500,
    modal: true,
    layout: 'fit',
    requires: [
        'devilry.extjshelpers.assignmentgroup.FileMetaBrowserPanel'
    ],

    config: {
        filemetastore: undefined,
        deliveryid: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'filemetabrowserpanel',
                border: false,
                filemetastore: this.filemetastore,
                deliveryid: this.deliveryid
            }]
        });
        this.callParent(arguments);
    }
});
