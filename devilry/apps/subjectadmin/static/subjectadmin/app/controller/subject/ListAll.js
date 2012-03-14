/**
 * Controller for the list of all subjects.
 */
Ext.define('subjectadmin.controller.subject.ListAll', {
    extend: 'Ext.app.Controller',

    views: [
        'subject.ListAll'
    ],

    stores: [
        'Subjects'
    ],

    refs: [{
        ref: 'subjectList',
        selector: 'subjectlistall #subjectList'
    }],

    init: function() {
        this.control({
            'viewport subjectlistall': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
        this.subject_shortname = this.getSubjectOverview().subject_shortname;
        this._loadSubject();
    }
});
