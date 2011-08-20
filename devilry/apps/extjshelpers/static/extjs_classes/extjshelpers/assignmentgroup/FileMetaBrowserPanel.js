
/**
 * Panel to browse FileMeta.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.FileMetaBrowserPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.filemetabrowserpanel',
    cls: 'widget-filemetabrowserpanel',

    config: {
        /**
         * @cfg
         * FileMeta ``Ext.data.Store``. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
         * class.
         */
        filemetastore: undefined,

        
        /**
         * @cfg
         * Id of the delivery in which the filemetas belong.
         */
        deliveryid: undefined,
    },

    initComponent: function() {
        this.filemetastore.proxy.extraParams.filters = Ext.JSON.encode([
            {field: 'delivery', comp:'exact', value: this.deliveryid}
        ]);

        this.filemetastore.load();
        
        //TODO Necessary. Get undefined when referenced later
        var stored_delivery_id = this.deliveryid;

        
        Ext.apply(this, {
            items: [{
                xtype: 'grid',
                store: this.filemetastore,
                columns: [{
                    header: 'File name', flex:1, dataIndex: 'filename'
                }, {
                    header: 'Size', dataIndex: 'size'
                }],
                    listeners: {
                    itemclick: function(self, record) {
                        var url = DevilrySettings.DEVILRY_MAIN_PAGE + "/student/show-delivery/filedownload/" + record.data.id;
                        window.open(url, 'download');
                    }
                }
    
            }],

            bbar: [{
                xtype: 'button',
                text: 'Download all files (zip)',
                listeners: {
                    click: function(view, record, item) {
                        var url = DevilrySettings.DEVILRY_MAIN_PAGE + "/student/show-delivery/compressedfiledownload/" + stored_delivery_id;
                        window.open(url, 'download');
                    }
                }
            }, {
                xtype: 'button',
                text: 'Download all files (tar.gz)',
                listeners: {
                    click: function() {
                        console.log('Downloading tar.gz some time in the future');
                    }
                }
            }]
        });
        this.callParent(arguments);
    }
});
