/**
 * The grid that shows tags on a single group.
 */
Ext.define('devilry_subjectadmin.view.managestudents.TagsInGroupGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.tagsingroupgrid',
    cls: 'tagsingroupgrid',
    hideHeaders: true,
    requires: [
        'Ext.XTemplate'
    ],

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            title: dtranslate('devilry_subjectadmin.managestudents.tags.title'),
            tools: [{
                xtype: 'splitbutton',
                iconCls: 'icon-add-16',
                itemId: 'addTag',
                menu: [{
                    text: dtranslate('devilry_extjsextras.removeall'),
                    itemId: 'removeAllTags',
                    iconCls: 'icon-delete-16'
                }]
            }],
            columns: [{
                header: 'Tag',
                flex: 1,
                dataIndex: 'tag'
            }, {
                xtype: 'actioncolumn',
                width: 20,
                items: [{
                    icon: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras/resources/icons/16x16/delete.png',
                    tooltip: dtranslate('devilry_subjectadmin.managestudents.remove_tag'),
                    handler: function(grid, rowIndex, colIndex) {
                        me._onRemove(rowIndex, colIndex);
                    },
                }]
            }]
        });
        this.callParent(arguments);
    },

    _onRemove: function(rowIndex, colIndex) {
        var record = this.getStore().getAt(rowIndex);
        this.fireEvent('removeTag', record);
    }
});
