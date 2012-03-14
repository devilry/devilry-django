/**
 * Controller for the subject overview.
 */
Ext.define('subjectadmin.controller.subject.Overview', {
    extend: 'Ext.app.Controller',

    mixins: {
        'loadSubject': 'subjectadmin.utils.LoadSubjectMixin'
    },

    views: [
        'subject.Overview',
        'ActionList'
    ],

    stores: [
        'Subjects'
    ],

    refs: [{
        ref: 'gradeEditorSidebarBox',
        selector: 'subjectoverview editablesidebarbox[itemId=gradeeditor]'
    }, {
        ref: 'actions',
        selector: 'subjectoverview #actions'
    }, {
        ref: 'subjectOverview',
        selector: 'subjectoverview'
    }],

    init: function() {
        this.control({
            'viewport subjectoverview': {
                render: this._onSubjectViewRender
            },
            'viewport subjectoverview editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            }
        });
    },

    _onSubjectViewRender: function() {
        this.subject_shortname = this.getSubjectOverview().subject_shortname;
        this.period_shortname = this.getSubjectOverview().period_shortname;
        this.subject_shortname = this.getSubjectOverview().subject_shortname;
        this.loadSubject();
    },
});
