Ext.define('devilry_subjectadmin.view.gradeeditor.ChooseGradeEditorGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.gradeeditorchoosegrid',
    cls: 'devilry_subjectadmin_gradeeditorchoosegrid bootstrap',
    requires: [
        'Ext.XTemplate',
        'Ext.selection.CheckboxModel'
    ],

    border: 1,
    frame: false,
    hideHeaders: true,
    store: 'GradeEditors',

    col1Tpl: [
        '<div style="white-space:normal !important;">',
            '<div><strong>{record.title}</strong></div>',
            '<div>{record.description}</div>',
        '</div>'
    ],

    initComponent: function() {
        this.col1TplCompiled = Ext.create('Ext.XTemplate', this.col1Tpl);
        this.selModel = Ext.create('Ext.selection.CheckboxModel', {
            mode: 'SINGLE'
        });
        Ext.apply(this, {
            columns: [{
                dataIndex: 'gradeeditorid',
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
    }
});
