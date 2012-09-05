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

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            columns: [{
                header: 'Tag',
                flex: 1,
                dataIndex: 'tag'
            }]
        });
        this.callParent(arguments);
    }
});
