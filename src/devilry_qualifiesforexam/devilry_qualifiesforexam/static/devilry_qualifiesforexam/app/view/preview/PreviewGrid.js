Ext.define('devilry_qualifiesforexam.view.preview.PreviewGrid', {
    extend: 'devilry_subjectadmin.view.periodoverview.PeriodOverviewGridBase',
    alias: 'widget.previewgrid',
    cls: 'devilry_qualifiesforexam_previewgrid bootstrap',

    firstAssignmentColumnIndex: 2,

    /**
     * @property {int[]} [passing_relatedstudentids_map]
     * Set by the controller, and used by ``this._renderQualifiesColumn()``.
     */

    store: 'RelatedStudents',

    qualifiesColTpl: [
        '<p class="qualifies">',
            '<tpl if="qualifies">',
                '<span class="qualified-for-exam label label-success">',
                    gettext('Yes'),
                '</span>',
            '<tpl else>',
                '<span class="not-qualified-for-exam label label-warning">',
                    gettext('No'),
                '</span>',
            '</tpl>',
        '</p>'
    ],

    setupColumns: function() {
        this.qualifiesColTplCompiled = Ext.create('Ext.XTemplate', this.qualifiesColTpl);
        this.columns.push({
            text: gettext('Qualifies for final exams?'),
            dataIndex: 'id',
            flex: 1,
            renderer: this._renderQualifiesColumn
        });
    },

    _renderQualifiesColumn: function(value, meta, record) {
        var relatedStudentId = record.get('relatedstudent').id;
        var qualifies = typeof this.passing_relatedstudentids_map[relatedStudentId] !== 'undefined';
        return this.qualifiesColTplCompiled.apply({
            qualifies: qualifies
        });
    }
});
