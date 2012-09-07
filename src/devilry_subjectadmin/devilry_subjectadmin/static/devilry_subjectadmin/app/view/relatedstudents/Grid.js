Ext.define('devilry_subjectadmin.view.relatedstudents.Grid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.relatedstudentsgrid',
    cls: 'devilry_subjectadmin_relatedusergrid devilry_subjectadmin_relatedstudentsgrid bootstrap',
    requires: [
        'Ext.XTemplate',
        'devilry_extjsextras.GridMultiSelectModel',
        'Ext.selection.CheckboxModel'
    ],

    store: 'RelatedStudents',
    border: 1,
    frame: false,
    hideHeaders: false,

    col1Tpl: [
        '<div class="meta_cell relateduserid_{record.id} relateduser_username_{record.user.username}">',
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
            '<tpl if="record.candidate_id">',
                '<div class="candidate_id">',
                    '{record.candidate_id}',
                '</div>',
            '</tpl>',
        '</div>'
    ],

    col2Tpl: [
        '<div class="tags_cell" style="white-space:normal !important;">',
            '{record.tags}',
        '</div>'
    ],

    initComponent: function() {
        this.col1TplCompiled = Ext.create('Ext.XTemplate', this.col1Tpl);
        this.col2TplCompiled = Ext.create('Ext.XTemplate', this.col2Tpl);
        Ext.apply(this, {
            selModel: Ext.create('devilry_extjsextras.GridMultiSelectModel'),
            columns: [{
                dataIndex: 'id',
                flex: 5,
                header: gettext('Student'),
                menuDisabled: true,
                renderer: this.renderCol1,
                sortable: false
            }, {
                dataIndex: 'tags',
                flex: 5,
                header: gettext('Tags'),
                menuDisabled: true,
                sortable: false,
                renderer: this.renderCol2
            }]
        });
        this.callParent(arguments);
    },

    renderCol1: function(unused, unused2, record) {
        return this.col1TplCompiled.apply({
            record: record.data
        });
    },
    renderCol2: function(unused, unused2, record) {
        return this.col2TplCompiled.apply({
            record: record.data
        });
    }
});
