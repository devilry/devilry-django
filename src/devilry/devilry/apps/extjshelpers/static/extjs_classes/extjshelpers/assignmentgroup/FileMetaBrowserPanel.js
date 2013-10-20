
/**
 * Panel to browse FileMeta.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.FileMetaBrowserPanel', {
    extend: 'Ext.view.View',
    alias: 'widget.filemetabrowserpanel',
    cls: 'widget-filemetabrowserpanel bootstrap',

    /**
     * @cfg {Ext.data.Store} [store]
     * FileMeta store. (Required).
     * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
     * class.
     */
    store: undefined,

    tpl: [
        '<h4>', gettext('Files'), ':</h4>',
        '<ul>',
            '<tpl for="files">',
                '<li class="filelinkitem">',
                    '<a href="{[this.getDownloadUrl(values.id)]}"><strong>{filename}</strong></a>',
                    ' <small class="muted">({[this.humanReadableSize(values.size)]})</small>',
                '</li>',
            '</tpl>',
        '</ul>',
        '<p><a class="btn" href="{downloadAllUrl}">',
            '<i class="icon-download"></i> ',
            gettext('Download all files (.zip)'),
        '</a></p>', {
            getDownloadUrl: function(id) {
                return Ext.String.format("{0}/student/show-delivery/filedownload/{1}",
                    DevilrySettings.DEVILRY_URLPATH_PREFIX, id);
            },
            humanReadableSize:function (size) {
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
                return sizeWithUnit;
            }
        }
    ],

    itemSelector: 'li.filelinkitem',

    loadFilesForDelivery :function (deliveryid) {
        this.deliveryid = deliveryid;
        this.store.proxy.extraParams.filters = Ext.JSON.encode([
            {field: 'delivery', comp:'exact', value: this.deliveryid}
        ]);
        this.store.load();
    },

    collectData : function(records, startIndex){
        var files = this.callParent(arguments);
        return {
            files: files,
            downloadAllUrl: Ext.String.format("{0}/student/show-delivery/compressedfiledownload/{1}",
                DevilrySettings.DEVILRY_URLPATH_PREFIX, this.deliveryid)
        };
    }
});
