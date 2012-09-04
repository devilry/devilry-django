Ext.define('devilry_subjectadmin.view.managestudents.SelectExaminersGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.selectexaminersgrid',
    cls: 'devilry_subjectadmin_selectexaminersgrid bootstrap',
    requires: [
        'Ext.XTemplate',
        'devilry_extjsextras.GridMultiSelectModel',
        'devilry_usersearch.ManageUsersGridModel',
        'Ext.selection.CheckboxModel'
    ],

    store: 'RelatedExaminersRo',
    border: 1,
    frame: false,
    hideHeaders: true,

    col1Tpl: [
        '<divclass="examinercell examinerid_{record.id}">',
            '<div class="full_name"><strong>{record.user.full_name}</strong></div>',
            '<div class="username">',
                '<small>{record.user.username}</small>',
            '</div>',
        '</div>'
    ],

    initComponent: function() {
        this.col1TplCompiled = Ext.create('Ext.XTemplate', this.col1Tpl);
        Ext.apply(this, {
            selModel: Ext.create('devilry_extjsextras.GridMultiSelectModel'),
            columns: [{
                dataIndex: 'id',
                flex: 1,
                menuDisabled: true,
                renderer: this.renderCol1,
                sortable: false
            }],
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
    }
});
