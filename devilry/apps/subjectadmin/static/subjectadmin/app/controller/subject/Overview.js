/**
 * Controller for the subject overview.
 */
Ext.define('subjectadmin.controller.subject.Overview', {
    extend: 'Ext.app.Controller',

    views: [
        'subject.Overview',
        'ActionList'
    ],

    stores: [
        'Subjects'
    ],

    refs: [{
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
        this._loadSubject();
    },

    _getMaskElement: function() {
        return this.getAssignmentOverview().getEl();
    },

    /** Load subject.
     * Calls ``this._onLoadSubjectSuccess(record)`` on success, and shows an
     * error on the ``this._getMaskElement()`` element on error.
     * */
    _loadSubject: function() {
        var store = this.getSubjectsStore();
        store.loadSubject(
            this.subject_shortname, this._onLoadSubject, this
        );
    },

    _onLoadSubject: function(records, operation) {
        if(operation.success) {
            this._onLoadSubjectSuccess(records[0]);
        } else {
            this._onLoadSubjectFailure(operation);
        }
    },

    _onLoadSubjectFailure: function(operation) {
        var tpl = Ext.create('Ext.XTemplate',
            '<h2>{title}</h2>',
            '<p>{subject_shortname}.{period_shortname}.{subject_shortname}</p>'
        );
        Ext.defer(function() { // NOTE: The delay is required for the mask to draw itself correctly.
            this._getMaskElement().mask(tpl.apply({
                title: dtranslate('themebase.doesnotexist'),
                subject_shortname: this.getSubjectShortname(),
                period_shortname: this.getPeriodShortname(),
                subject_shortname: this.getSubjectShortname()
            }), 'messagemask');
        }, 50, this);
    },

    _onLoadSubjectSuccess: function(record) {
        this.assignmentRecord = record;
        //this.application.fireEvent('subjectSuccessfullyLoaded', record);
        this.getActions().setTitle(record.get('long_name'));
    },
});
