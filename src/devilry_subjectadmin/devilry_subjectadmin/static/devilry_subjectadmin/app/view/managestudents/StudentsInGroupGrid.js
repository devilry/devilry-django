/**
 * The grid that shows students on a single group.
 */
Ext.define('devilry_subjectadmin.view.managestudents.StudentsInGroupGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.studentsingroupgrid',
    cls: 'studentsingroupgrid',
    hideHeaders: true,
    requires: [
        'Ext.XTemplate',
        'devilry_theme.Icons'
    ],

    rowTpl: [
        '<tpl if="user.full_name">',
            '{user.full_name} <small>({user.username})</small>',
        '</tpl>',
        '<tpl if="!user.full_name">',
            '{user.username}',
        '</tpl>'
    ],

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            title: gettext('Students'),
            columns: [{
                header: 'Name',
                flex: 1,
                dataIndex: 'id',
                renderer: function(unused1, unused2, studentRecord) {
                    return Ext.create('Ext.XTemplate', this.rowTpl).apply(studentRecord.data);
                }
            }, {
                xtype: 'actioncolumn',
                width: 20,
                items: [{
                    icon: devilry_theme.Icons.DELETE_SMALL,
                    tooltip: gettext('Remove student from project group'),
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
        this.fireEvent('removeStudent', record);
    }
});
