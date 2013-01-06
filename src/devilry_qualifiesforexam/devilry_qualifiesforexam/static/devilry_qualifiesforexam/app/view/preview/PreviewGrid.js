Ext.define('devilry_qualifiesforexam.view.preview.PreviewGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.previewgrid',
    cls: 'devilry_qualifiesforexam_previewgrid bootstrap',

    /**
     * @cfg {int} [firstAssignmentColumnIndex=1]
     * When rendering assignment result, we need to know the column index of the first assignment
     * to place the results in the correct column.
     */
    firstAssignmentColumnIndex: 2,

    /**
     * @property {int[]} [passing_relatedstudentids_map]
     * Set by the controller, and used by ``this._renderQualifiesColumn()``.
     */


    store: 'RelatedStudents',
    requires: [
        'Ext.XTemplate',
        'Ext.grid.column.Column'
    ],

    studentColTpl: [
        '<div class="student" style="white-space: normal !important;">',
            '<div class="fullname"><strong>{full_name}</strong></div>',
            '<div class="username"><small class="muted">{username}</small></div>',
        '</div>'
    ],
    feedbackColTpl: [
        '<div class="feedback feedback_assignment_{assignmentid}" style="white-space: normal !important;">',
            '<tpl if="grouplist.length == 0">',
                '<small class="muted nofeedback">',
                    gettext('Not registered on assignment'),
                '</small>',
            '<tpl else>',
                '<tpl for="grouplist">',
                    '<div class="group-{id}">',
                        '<div class="status-{status}">',
                            '<tpl if="status === \'corrected\'">',
                                '<div class="{[this.getGradeClass(values.feedback.is_passing_grade)]}">',
                                    '<div class="passingstatus {[this.getTextClassForGrade(values.feedback.is_passing_grade)]}">',
                                        '{[this.getPassedOrFailedText(values.feedback.is_passing_grade)]}',
                                    '</div>',
                                    '<div class="gradedetails">',
                                        '<small class="grade muted">({feedback.grade})</small>',
                                        ' <small class="points muted">(',
                                            gettext('Points:'),
                                            '{feedback.points})',
                                        '</small>',
                                    '</div>',
                                '</div>',
                            '<tpl elseif="status === \'waiting-for-deliveries\'">',
                                '<em><small class="muted">', gettext('Waiting for deliveries'), '</small></em>',
                            '<tpl elseif="status === \'waiting-for-feedback\'">',
                                '<em><small class="muted">', gettext('Waiting for feedback'), '</small></em>',
                            '<tpl else>',
                                '<span class="label label-important">{status}</span>',
                            '</tpl>',
                        '</div>',
                    '</div>',
                '</tpl>',
            '</tpl>',
        '</div>', {
            getGradeClass: function(is_passing_grade) {
                return is_passing_grade? 'passinggrade': 'notpassinggrade';
            },
            getTextClassForGrade: function(is_passing_grade) {
                return is_passing_grade? 'text-success': 'text-warning';
            },
            getPassedOrFailedText: function(is_passing_grade) {
                return is_passing_grade? gettext('Passed'): gettext('Failed');
            }
        }
    ],

    initComponent: function() {
        this.studentColTplCompiled = Ext.create('Ext.XTemplate', this.studentColTpl);
        this.feedbackColTplCompiled = Ext.create('Ext.XTemplate', this.feedbackColTpl);
        this.columns = [{
            text: gettext('Student'),
            dataIndex: 'id',
            flex: 2,
            renderer: this.renderStudentColumn
        }];
        this.setupColumns();
        this.callParent(arguments);
    },

    renderStudentColumn: function(value, meta, record) {
        return this.studentColTplCompiled.apply(record.get('user'));
    },

    /**
     * Add assignment column to the grid.
     * @param assignment An object with assignment details.
     *
     * NOTE: Remember to call ``getView().refresh()`` on the grid after adding new dynamic columns.
     */
    addAssignmentResultColumn: function(assignment) {
        var column = Ext.create('Ext.grid.column.Column', {
            text: assignment.short_name,
            flex: 1,
            dataIndex: 'id',
            renderer: this._renderAssignmentResultColum
        });
        this.headerCt.insert(this.columns.length, column);
    },


    _renderAssignmentResultColum: function(value, meta, record, rowIndex, colIndex) {
        var assignmentIndex = colIndex - this.firstAssignmentColumnIndex;
        var assignmentinfo = record.get('groups_by_assignment')[assignmentIndex];
        return this.feedbackColTplCompiled.apply({
            grouplist: assignmentinfo.grouplist,
            assignmentid: assignmentinfo.assignmentid
        });
    },


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
