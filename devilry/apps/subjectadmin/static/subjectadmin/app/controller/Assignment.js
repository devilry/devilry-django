/**
 * Controller for the assignment overview.
 */
Ext.define('subjectadmin.controller.Assignment', {
    extend: 'Ext.app.Controller',

    //requires: [
    //],
    views: [
        'assignment.Assignment',
        'ActionList'
    ],

    stores: [
        'SingleAssignment'
    ],

    refs: [{
        ref: 'gradeEditorSidebarBox',
        selector: 'editablesidebarbox[itemId=gradeeditor]'
    }, {
        ref: 'publishingTimeSidebarBox',
        selector: 'editablesidebarbox[itemId=publishingtime]'
    }, {
        ref: 'assignmentView',
        selector: 'assignment'
    }],

    init: function() {
        this.control({
            'viewport assignment editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            },
            'viewport assignment editablesidebarbox[itemId=publishingtime] button': {
                click: this._onEditPublishingTime
            }
        });
    },

    onLaunch: function() {
        this.subject_shortname = this.getAssignmentView().subject_shortname;
        this.period_shortname = this.getAssignmentView().period_shortname;
        this.assignment_shortname = this.getAssignmentView().assignment_shortname;
        this._loadAssignment();
    },

    _loadAssignment: function() {
        var store = this.getSingleAssignmentStore();
        store.loadAssignment(
            this.subject_shortname, this.period_shortname, this.assignment_shortname,
            this._onLoadAssignment, this
        );
    },

    _onLoadAssignment: function(records, operation) {
        console.log(records);
        console.log(operation);
    },

    _onEditGradeEditor: function() {
        console.log('grade', this.getGradeEditorSidebarBox());
    },

    _onEditPublishingTime: function() {
        console.log('pub', this.getPublishingTimeSidebarBox());
    },
});
