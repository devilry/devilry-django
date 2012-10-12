Ext.define('devilry_subjectadmin.controller.assignment.EditGradeEditor', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.LoadGradeEditorMixin'
    ],

    requires: [
        'devilry.gradeeditors.ConfigEditorWidget',
        'devilry_subjectadmin.utils.UrlLookup',
        'Ext.window.MessageBox'
    ],

    views: [
        'assignment.GradeEditorSelectWidget'
    ],

    models: [
        'GradeEditorConfig',
        'GradeEditorRegistryItem'
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
        this.loadGradeEditorRecords(assignmentRecord.get('id'));
    },

    onLoadGradeEditorSuccess: function(gradeEditorConfigRecord, gradeEditorRegistryItemRecord) {
        this.getGradeEditorSelectWidget().enable();
        this.gradeEditorConfigRecord = gradeEditorConfigRecord;
        this.gradeEditorRegistryItemRecord = gradeEditorRegistryItemRecord;
        this._updateWidget();
    },


    _onEdit: function() {
        this.application.route.navigate(
            devilry_subjectadmin.utils.UrlLookup.editGradeEditor(
                this.assignmentRecord.get('id')));
    },


    _isConfigurable: function () {
        return this.gradeEditorRegistryItemRecord.isConfigurable();
    },

    _isMissingGradeEditorConfig: function() {
        return this._isConfigurable() && !this.gradeEditorConfigRecord.hasConfig();
    },

    _updateWidget: function() {
        var title, body;
        var editurl = devilry_subjectadmin.utils.UrlLookup.editGradeEditor(
            this.assignmentRecord.get('id'));
        this.getGradeEditorSelectWidget().updateTitle(gettext('Grading system'), editurl);
        var config_editor_url = this.gradeEditorRegistryItemRecord.get('config_editor_url');
        this.getReadOnlyViewBody().update({
            title: this.gradeEditorRegistryItemRecord.get('title'),
            //description: this.gradeEditorRegistryItemRecord.get('description'),
            isMissingConfig: this._isMissingGradeEditorConfig(),
            configurable: this._isConfigurable()
        });
    }
});
