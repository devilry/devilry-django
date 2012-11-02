/**
 * The grid that shows examiners on a single group.
 */
Ext.define('devilry_subjectadmin.view.managestudents.ExaminersInGroupGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.examinersingroupgrid',
    cls: 'devilry_subjectadmin_examinersingroupgrid',
    hideHeaders: true,
    disableSelection: true,
    border: false,
    requires: [
        'Ext.XTemplate'
    ],
    store: 'SingleGroupExaminers',

    rowTpl: [
        '<div class="examinersingroupgrid_meta examinersingroupgrid_meta_{user.username}">',
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
        var rowTplCompiled = Ext.create('Ext.XTemplate', this.rowTpl);
        Ext.apply(this, {
            columns: [{
                header: 'Name',
                flex: 1,
                dataIndex: 'id',
                renderer: function(unused1, unused2, examinerRecord) {
                    return rowTplCompiled.apply(examinerRecord.data);
                }
            }]
        });
        this.callParent(arguments);
    }
});
