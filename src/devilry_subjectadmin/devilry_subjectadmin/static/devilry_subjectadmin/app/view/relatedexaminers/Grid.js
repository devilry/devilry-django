Ext.define('devilry_subjectadmin.view.relatedexaminers.Grid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.relatedexaminersgrid',
    cls: 'devilry_subjectadmin_relatedusergrid devilry_subjectadmin_relatedexaminersgrid bootstrap',

    requires: [
        'Ext.XTemplate',
        'devilry_extjsextras.GridBigButtonCheckboxModel',
        'Ext.selection.CheckboxModel'
    ],

    store: 'RelatedExaminers',
    border: 1,
    frame: false,
    hideHeaders: false,
    multiSelect: true,

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
                '<small class="muted">{record.user.username}</small>',
            '</div>',
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
            selModel: Ext.create('devilry_extjsextras.GridBigButtonCheckboxModel'),
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
        this.initExtra();
        this.callParent(arguments);
    },

    initExtra: function() {
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
