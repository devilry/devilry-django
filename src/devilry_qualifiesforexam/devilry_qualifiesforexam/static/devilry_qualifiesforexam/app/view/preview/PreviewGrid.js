Ext.define('devilry_qualifiesforexam.view.preview.PreviewGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.previewgrid',
    cls: 'devilry_qualifiesforexam_previewgrid bootstrap',

    /**
     * @cfg {String[]} [assignments]
     */

    store: 'RelatedStudents',
    requires: [
        'Ext.XTemplate'
    ],

    studentColTpl: [
        '<div class="student" style="white-space: normal !important;">',
            '<div class="fullname"><strong>{full_name}</strong></div>',
            '<div class="username"><small class="muted">{username}</small></div>',
        '</div>'
    ],

    initComponent: function() {
        this.studentColTplCompiled = Ext.create('Ext.XTemplate', this.studentColTpl);
        this.columns = [{
            text: gettext('Student'),
            dataIndex: 'id',
            flex: 3,
            renderer: this._renderStudentColumn
        }];
        this.callParent(arguments);
    },

    _renderStudentColumn: function(value, meta, record) {
        return this.studentColTplCompiled.apply(record.get('user'));
    }
});
