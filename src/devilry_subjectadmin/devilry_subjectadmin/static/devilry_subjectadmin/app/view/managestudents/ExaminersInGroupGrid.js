/**
 * The grid that shows examiners on a single group.
 */
Ext.define('devilry_subjectadmin.view.managestudents.ExaminersInGroupGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.examinersingroupgrid',
    cls: 'examinersingroupgrid',
    hideHeaders: true,
    disableSelection: true,
    border: false,
    requires: [
        'Ext.XTemplate',
        'devilry_theme.Icons'
    ],

    rowTpl: [
        '<div class="examinersingroupgrid_meta examinersingroupgrid_meta_{user.username}">',
            '<div class="fullname">',
                '<tpl if="user.full_name">',
                    '<div>{user.full_name}</div>',
                '<tpl else>',
                    '<em class="nofullname">', gettext('Full name missing'), '</em>',
                '</tpl>',
            '</div>',
            '<div class="username"><small>{user.username}</small></div>',
        '</div>'
    ],

    initComponent: function() {
        var me = this;
        var rowTplCompiled = Ext.create('Ext.XTemplate', this.rowTpl);
        Ext.apply(this, {
            columns: [{
                header: 'Name',
                flex: 1,
                dataIndex: 'id',
                renderer: function(unused1, unused2, examinerRecord) {
                    return rowTplCompiled.apply(examinerRecord.data);
                }
            }, {
                xtype: 'actioncolumn',
                width: 20,
                items: [{
                    icon: devilry_theme.Icons.DELETE_SMALL,
                    tooltip: gettext('Remove examiner from group.'),
                    handler: function(grid, rowIndex, colIndex) {
                        me._onRemove(rowIndex, colIndex);
                    },
                    getClass: function(unused, unused2, record) {
                        return Ext.String.format(
                            'devilry_clickable_icon examinersingroupgrid_remove examinersingroupgrid_remove_{0}',
                            record.get('user').username);
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    _onRemove: function(rowIndex, colIndex) {
        var record = this.getStore().getAt(rowIndex);
        this.fireEvent('removeExaminer', record);
    }
});
