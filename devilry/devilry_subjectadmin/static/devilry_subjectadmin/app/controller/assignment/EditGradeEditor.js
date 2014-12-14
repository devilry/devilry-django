Ext.define('devilry_subjectadmin.controller.assignment.EditGradeEditor', {
    extend: 'Ext.app.Controller',

    requires: [
        'devilry_subjectadmin.utils.UrlLookup',
        'Ext.window.MessageBox'
    ],

    views: [
        'assignment.GradeEditorSelectWidget'
    ],

    refs: [{
        ref: 'gradeEditorSelectWidget',
        selector: 'gradeeditorselect-widget'
    }, {
        ref: 'readOnlyViewBody',
        selector: 'gradeeditorselect-widget markupmoreinfobox'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            assignmentSuccessfullyLoaded: this._onLoadAssignment
        });
        this.control({
            'gradeeditorselect-widget': {
                edit: this._onEdit
            }
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        //has_valid_grading_setup
        this.getGradeEditorSelectWidget().enable();
        this._updateWidget();
    },

    _onEdit: function() {
        window.location.href = devilry_subjectadmin.utils.UrlLookup.editGradeEditor(
                this.assignmentRecord.get('id'));
    },

    _isMissingGradeEditorConfig: function() {
        return this._isConfigurable() && !this.gradeEditorConfigRecord.hasConfig();
    },

    _updateWidget: function() {
        var title, body;
        var editurl = devilry_subjectadmin.utils.UrlLookup.editGradeEditor(
            this.assignmentRecord.get('id'));
        this.getGradeEditorSelectWidget().updateTitle(gettext('Grading system'), editurl);
        this.getReadOnlyViewBody().update({
            title: this.assignmentRecord.get('gradingsystemplugin_title'),
            has_valid_grading_setup: this.assignmentRecord.get('has_valid_grading_setup')
        });
    }
});
