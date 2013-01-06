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
            menuDisabled: true,
            sortable: false,
            renderer: this._renderQualifiesColumn
        });
    },

    _qualifiesForFinalExam: function(record) {
        var relatedStudentId = record.get('relatedstudent').id;
        var qualifies = typeof this.passing_relatedstudentids_map[relatedStudentId] !== 'undefined';
        return qualifies;
    },

    _renderQualifiesColumn: function(value, meta, record) {
        return this.qualifiesColTplCompiled.apply({
            qualifies: this._qualifiesForFinalExam(record)
        });
    },

    setupToolbar: function() {
        this.callParent(arguments);
        this.tbar[0].menu.push({
            text: gettext('Qualifies for final exam'),
            hideOnClick: false,
            menu: [{
                text: gettext('Qualified students first'),
                listeners: {
                    scope: this,
                    click: this.sortByQualifiesQualifiedFirst
                }
            }, {
                text: gettext('Qualified students last'),
                listeners: {
                    scope: this,
                    click: this.sortByQualifiesQualifiedLast
                }
            }]
        });
    },

    _sortByQualifies: function(descending) {
        var sorter = function(a, b) { return a - b; };
        if(descending) {
            sorter = function(a, b) { return b - a; };
        }
        this.getStore().sort(Ext.create('Ext.util.Sorter', {
            sorterFn: Ext.bind(function(a, b) {
                return sorter(Number(this._qualifiesForFinalExam(a)), Number(this._qualifiesForFinalExam(b)));
            }, this)
        }));
    },
    sortByQualifiesQualifiedFirst: function() {
        return this._sortByQualifies(true);
    },
    sortByQualifiesQualifiedLast: function() {
        return this._sortByQualifies(false);
    }
});
