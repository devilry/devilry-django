Ext.define('devilry_subjectadmin.view.managestudents.SelectExaminersGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.selectexaminersgrid',
    cls: 'devilry_subjectadmin_selectexaminersgrid bootstrap',
    requires: [
        'Ext.XTemplate',
        'devilry_usersearch.ManageUsersGridModel',
        'devilry_subjectadmin.view.managestudents.SelectGroupsBySearchWidget',
        'devilry_extjsextras.GridBigButtonCheckboxModel'
    ],

    store: 'RelatedExaminersRo',
    border: 1,
    frame: false,
    hideHeaders: true,

    col1Tpl: [
        '<div class="examinercell examinerid_{record.id} examiner_username_{record.user.username}">',
            '<div class="full_name">',
                '<tpl if="record.user.full_name">',
                    '<strong>{record.user.full_name}</strong>',
                '<tpl else>',
                    '<em class="nofullname">', gettext('Full name missing'), '</em>',
                '</tpl>',
            '</div>',
            '<div class="username">',
                '<small>{record.user.username}</small>',
            '</div>',
        '</div>'
    ],

    initComponent: function() {
        this.col1TplCompiled = Ext.create('Ext.XTemplate', this.col1Tpl);
        Ext.apply(this, {
            selModel: Ext.create('devilry_extjsextras.GridBigButtonCheckboxModel'),
            columns: [{
                dataIndex: 'id',
                flex: 1,
                menuDisabled: true,
                renderer: this.renderCol1,
                sortable: false
            }]
        });
        this.callParent(arguments);
    },

    renderCol1: function(unused, unused2, record) {
        return this.col1TplCompiled.apply({
            record: record.data
        });
    },

    
    getSelectedAsUserStore: function() {
        var selection = this.getSelectionModel().getSelection();
        var users = [];
        Ext.Array.each(selection, function(relatedExaminerRecord) {
            var user = relatedExaminerRecord.get('user');
            users.push(user);
        }, this);

        return Ext.create('Ext.data.Store', {
            model: 'devilry_usersearch.ManageUsersGridModel',
            data: users
        });
    },

    selectUsersById: function(userIds) {
        var store = this.getStore();
        var records = [];
        Ext.Array.each(userIds, function(userId) {
            var index = store.findBy(function(record) {
                return record.get('user').id == userId;
            }, this);
            if(index > -1) {
                var record = store.getAt(index);
                records.push(record);
            }
        }, this);
        var selModel = this.getSelectionModel();
        selModel.select(records);
    }
});
