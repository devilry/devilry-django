/**
 * The grid that shows tags on a single group.
 */
Ext.define('devilry_subjectadmin.view.managestudents.TagsInGroupGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.tagsingroupgrid',
    cls: 'tagsingroupgrid',
    hideHeaders: true,
    disableSelection: true,
    border: false,
    requires: [
        'Ext.XTemplate'
    ],
    store: 'SingleGroupTags',

    rowTpl: [
        '<div class="tagsingroupgrid_tag tagsingroupgrid_tag_{tag}">',
            '{tag}',
        '</div>'
    ],

    initComponent: function() {
        var rowTplCompiled = Ext.create('Ext.XTemplate', this.rowTpl);
        var me = this;
        Ext.apply(this, {
            columns: [{
                header: 'Tag',
                flex: 1,
                dataIndex: 'tag',
                renderer: function(unused1, unused2, tagRecord) {
                    return rowTplCompiled.apply(tagRecord.data);
                }
            }]
        });
        this.callParent(arguments);
    }
});
