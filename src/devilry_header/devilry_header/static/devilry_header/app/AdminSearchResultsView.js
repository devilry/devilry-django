Ext.define('devilry_header.AdminSearchResultsView', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.devilry_header_adminsearchresults',
    cls: 'devilry_header_adminsearchresults bootstrap',
    requires: [
        'Ext.XTemplate'
    ],

    resultTpl: [
        '<div><strong class="title">{title}</strong> ({type})</div>',
        '<div class="muted"><small class="path">{path}</small></div>'
    ],

    hidden: true, // We show ourself automatically on search results
    hideHeaders: true,

    initComponent: function() {
        this.resultTplCompiled = Ext.create('Ext.XTemplate', this.resultTpl);
        Ext.apply(this, {
            minHeight: 50,
            columns: [{
                dataIndex: 'title',
                flex: 1,
                menuDisabled: true,
                renderer: this._renderResult,
                sortable: false
            }]
        });
        this.callParent(arguments);
    },

    search:function (search) {
        this.show();
        this.getStore().search({
            search: search
        }, {
            callback:function (records, op) {
                if(op.success) {
                }
            }
        });
    },

    _renderResult:function (unused, unused2, record) {
        return this.resultTplCompiled.apply(record.data);
    }
});
