
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

        this.on('render', function() {
            Ext.defer(function() {
                if(this.filemetastore.loading) {
                    this.setLoading(true);
                }
            }, 100, this);
        });
        this.filemetastore.load({
            scope: this,
            callback: function() {
                this.setLoading(false);
            }
        });
        
        Ext.apply(this, {
            items: [{
                xtype: 'grid',
                sortableColumns: false,
                store: this.filemetastore,
                cls: 'selectable-grid',
                columns: [{
                    header: 'File name',
                    menuDisabled: true,
                    flex:1, 
                    dataIndex: 'filename'
                }, {
                    header: 'Size',
                    menuDisabled: true,
                    dataIndex: 'size',
                    renderer: function(value) {
                        var units = ['Bytes', 'KBytes', 'MBytes', 'GBytes'];
                        var i = 0;
                        while(value >= 1024) {
                            value /= 1024;
                            ++i;
                        }
                        if(i < units.length) {
                            return value.toFixed() + ' ' + units[i];
                        } else {
                            return value + ' ' + units[0];
                        }
                        
                    }
                }],
                listeners: {
                    scope: this,
                    itemclick: function(self, record) {
                        var url = DevilrySettings.DEVILRY_URLPATH_PREFIX + "/student/show-delivery/filedownload/" + record.get('id');
                        window.open(url, 'download');
                    }
                }
    
            }],

            bbar: [{
                xtype: 'button',
                scale: 'large',
                text: 'Download all files (.zip)',
                listeners: {
                    scope: this,
                    click: function(view, record, item) {
                        var url = Ext.String.format(
                            '{0}/student/show-delivery/compressedfiledownload/{1}',
                            DevilrySettings.DEVILRY_URLPATH_PREFIX, this.deliveryid
                        );
                        window.open(url, 'download');
                    }
                }
            }]
            // , {
                // xtype: 'button',
                // text: 'Download all files (tar.gz)',
                // listeners: {
                    // click: function() {
                        // console.log('Downloading tar.gz some time in the future');
                    // }
                // }
            // }]
        });
        this.callParent(arguments);
    }
});
