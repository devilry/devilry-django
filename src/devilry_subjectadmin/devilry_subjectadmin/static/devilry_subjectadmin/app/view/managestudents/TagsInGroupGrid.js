/**
 * The grid that shows tags on a single group.
 */
Ext.define('devilry_subjectadmin.view.managestudents.TagsInGroupGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.tagsingroupgrid',
    cls: 'tagsingroupgrid',
    hideHeaders: true,
    disableSelection: true,
    requires: [
        'Ext.XTemplate',
        'devilry_theme.Icons'
    ],

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            title: gettext('Tags'),
            tools: [{
                xtype: 'splitbutton',
                icon: devilry_theme.Icons.ADD_SMALL,
                itemId: 'addTag',
                menu: [{
                    text: gettext('Remove all'),
                    itemId: 'removeAllTags',
                    icon: devilry_theme.Icons.DELETE_SMALL
                }]
            }, {
                xtype: 'button',
                margin: '0 0 0 3',
                icon: devilry_theme.Icons.HELP_SMALL,
            }],
            columns: [{
                header: 'Tag',
                flex: 1,
                dataIndex: 'tag'
            }, {
                xtype: 'actioncolumn',
                width: 20,
                items: [{
                    icon: devilry_theme.Icons.DELETE_SMALL,
                    tooltip: gettext('Remove tag'),
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
