
/**
 * Panel to browse FileMeta.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.FileMetaBrowserPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.filemetabrowserpanel',
    cls: 'widget-filemetabrowserpanel',

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

    fileTpl: [
        '<a href="{downloadurl}"><strong>{data.filename}</strong></a> <small class="muted">({size})</small>'
    ],

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

        var renderTpl = Ext.create('Ext.XTemplate', this.fileTpl);
        var me = this;
        Ext.apply(this, {
            items: [{
                xtype: 'grid',
                sortableColumns: false,
                store: this.filemetastore,
                hideHeaders: true,
                disableSelection: true,
                cls: 'bootstrap',
                columns: [{
                    flex:1,
                    menuDisabled: true,
                    dataIndex: 'size',
                    renderer: function(size, unused, record) {
                        var units = ['Bytes', 'KBytes', 'MBytes', 'GBytes'];
                        var i = 0;
                        while(size >= 1024) {
                            size /= 1024;
                            ++i;
                        }
                        var sizeWithUnit;
                        if(i < units.length) {
                            sizeWithUnit = size.toFixed() + ' ' + units[i];
                        } else {
                            sizeWithUnit = size + ' ' + units[0];
                        }

                        var url = Ext.String.format("{0}/student/show-delivery/filedownload/{1}",
                            DevilrySettings.DEVILRY_URLPATH_PREFIX, record.get('id'));
                        return renderTpl.apply({
                            data: record.data,
                            size: sizeWithUnit,
                            downloadurl: url
                        });
                    }
                }]
//                listeners: {
//                    scope: this,
//                    itemclick: function(self, record) {
//                        var url = DevilrySettings.DEVILRY_URLPATH_PREFIX + "/student/show-delivery/filedownload/" + record.get('id');
//                        window.open(url, 'download');
//                    }
//                }
    
            }],

            bbar: [{
                xtype: 'button',
                scale: 'large',
                text: gettext('Download all files (.zip)'),
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
        });
        this.callParent(arguments);
    }
});
