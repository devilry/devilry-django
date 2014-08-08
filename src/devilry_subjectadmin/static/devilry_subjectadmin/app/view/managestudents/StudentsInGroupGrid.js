/**
 * The grid that shows students on a single group.
 */
Ext.define('devilry_subjectadmin.view.managestudents.StudentsInGroupGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.studentsingroupgrid',
    cls: 'devilry_subjectadmin_studentsingroupgrid',
    hideHeaders: true,
    disableSelection: true,
    border: false,
    requires: [
        'Ext.XTemplate',
        'devilry_theme.Icons'
    ],
    store: 'SingleGroupCandidates',

    rowTpl: [
        '<div class="studentsingroupgrid_meta studentsingroupgrid_meta_{user.username}">',
            '<div class="fullname">',
                '<tpl if="user.full_name">',
                    '<div>{user.full_name}</div>',
                '<tpl else>',
                    '<em class="nofullname">', gettext('Full name missing'), '</em>',
                '</tpl>',
            '</div>',
            '<div class="username"><small class="muted">{user.username}</small></div>',
        '</div>'
    ],

    initComponent: function() {
        var me = this;
        this.columns = [{
            header: 'Name',
            flex: 1,
            dataIndex: 'id',
            renderer: function(unused1, unused2, studentRecord) {
                return Ext.create('Ext.XTemplate', this.rowTpl).apply(studentRecord.data);
            }
        }];
        //if(this.getStore().getCount() > 1) {
            this.columns.push({
                xtype: 'actioncolumn',
                itemId: 'deleteColumn',
                width: 20,
                hidden: true,
                items: [{
                    icon: devilry_theme.Icons.DELETE_SMALL,
                    tooltip: gettext('Move the student from this project group into a copy of this group. Copies deadlines, deliveries, feedback, tags and examiners.'),
                    handler: function(grid, rowIndex, colIndex) {
                        me._onRemove(rowIndex, colIndex);
                    },
                    getClass: function(unused, unused2, record) {
                        return Ext.String.format(
                            'devilry_clickable_icon studentsingroupgrid_pop studentsingroupgrid_pop_{0}',
                            record.get('user').username);
                    }
                }]
            });
        //}
        this.callParent(arguments);
    },

    hideDeleteColumn: function() {
        this.down('#deleteColumn').hide();
    },
    showDeleteColumn: function() {
        this.down('#deleteColumn').show();
    },

    _onRemove: function(rowIndex, colIndex) {
        var record = this.getStore().getAt(rowIndex);
        this.fireEvent('popStudent', record);
    }
});
