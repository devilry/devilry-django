/**
 * The grid that shows examiners on a single group.
 */
Ext.define('devilry_subjectadmin.view.managestudents.ExaminersInGroupGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.examinersingroupgrid',
    cls: 'examinersingroupgrid',
    hideHeaders: true,
    requires: [
        'Ext.XTemplate'
    ],

    rowTpl: [
        '<tpl if="user__devilryuserprofile__full_name">',
            '{user__devilryuserprofile__full_name} <small>({user__username})</small>',
        '</tpl>',
        '<tpl if="!user__devilryuserprofile__full_name">',
            '{user__username}',
        '</tpl>'
    ],

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            title: dtranslate('devilry_subjectadmin.managestudents.examiners.title'),
            tools: [{
                xtype: 'splitbutton',
                iconCls: 'icon-add-16',
                itemId: 'addExaminer',
                menu: [{
                    text: dtranslate('devilry_extjsextras.removeall'),
                    itemId: 'removeAllExaminers',
                    iconCls: 'icon-delete-16'
                }]
            }],
            columns: [{
                header: 'Name',
                flex: 1,
                dataIndex: 'user__devilryuserprofile__full_name',
                renderer: function(unused1, unused2, examinerRecord) {
                    return Ext.create('Ext.XTemplate', this.rowTpl).apply(examinerRecord.data);
                }
            }, {
                xtype: 'actioncolumn',
                width: 20,
                items: [{
                    icon: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras/resources/icons/16x16/delete.png',
                    tooltip: dtranslate('devilry_subjectadmin.managestudents.remove_examiner'),
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
        this.fireEvent('removeExaminer', record);
    }
});
