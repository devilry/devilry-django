Ext.define('devilry_subjectadmin.controller.assignment.EditGradeEditor', {
    extend: 'Ext.app.Controller',

    views: [
        'assignment.GradeEditorSelectWindow',
        'assignment.GradeEditorSelectWidget'
    ],

    controllers: [
        'assignment.Overview'
    ],

    models: [
        'GradeEditorConfig',
        'GradeEditorRegistryItem'
    ],

    refs: [{
        ref: 'gradeEditorSelectWindow',
        selector: 'gradeeditorselectwindow'
    }, {
        ref: 'gradeEditorSelectWidget',
        selector: 'gradeeditorselect-widget'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            assignmentSuccessfullyLoaded: this._onLoadAssignment
        });
        this.control({
            'gradeeditorselectwindow savebutton': {
                click: this._onSave
            },
            'gradeeditorselectwindow cancelbutton': {
                click: this._closeSelectWindow
            },
            'gradeeditorselect-widget': {
                edit: this._onEdit
            }
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this._loadGradeEditorConfig();
    },


    //
    //
    // Load the editor and the registry item
    //
    //

    _loadGradeEditorConfig: function() {
        this.getGradeEditorConfigModel().load(this.assignmentRecord.get('id'), {
            scope: this,
            success: this._onLoadGradeEditorConfigSuccess,
            failure: function() {
                console.log('failed');
            }
        });
    },

    _onLoadGradeEditorConfigSuccess: function(gradeEditorConfigRecord, op) {
        this.gradeEditorConfigRecord = gradeEditorConfigRecord;
        console.log('GradeEditorConfig:', gradeEditorConfigRecord.data);
        this._loadGradeEditorRegistryItem(gradeEditorConfigRecord.get('gradeeditorid'));
    },

    _loadGradeEditorRegistryItem: function(gradeeditorid) {
        this.getGradeEditorRegistryItemModel().load(gradeeditorid, {
            scope: this,
            success: this._onLoadGradeEditorRegistryItemSuccess,
            failure: function() {
                console.log('failed GradeEditorRegistryItem');
            }
        });
    },
    _onLoadGradeEditorRegistryItemSuccess: function(gradeEditorRegistryItemRecord, op) {
        this.gradeEditorRegistryItemRecord = gradeEditorRegistryItemRecord;
        console.log('GradeEditorRegistryItem:', gradeEditorRegistryItemRecord.data);
        this.getGradeEditorSelectWidget().enable();
        this._updateWidget();
    },


    //
    //
    // The GradeEditorSelectWindow
    //
    //

    _onEdit: function() {
        Ext.widget('gradeeditorselectwindow').show();
    },

    _closeSelectWindow: function() {
        this.getGradeEditorSelectWindow().close();
    },

    _onSave: function() {
        console.log('Save');
    },

    _getMaskElement: function() {
        return this.getGradeEditorSelectWindow().getEl();
    },

    _onSaveSuccess: function() {
        this._getMaskElement().unmask();
        this._closeSelectWindow();
        this._updateWidget();
    },


    //
    //
    // The widget
    //
    //

    _isMissingGradeEditorConfig: function() {
        var config = this.gradeEditorConfigRecord.get('config');
        var config_editor_url = this.gradeEditorRegistryItemRecord.get('config_editor_url');
        return Ext.isEmpty(config) && !Ext.isEmpty(config_editor_url);
    },

    _updateWidget: function() {
        console.log('update');
        var title, body;

        this.getGradeEditorSelectWidget().updateTitle([
            gettext('Grade editor'), ': ',
            '<em>',
                Ext.String.ellipsis(this.gradeEditorRegistryItemRecord.get('title'), 20),
            '</em>'
        ].join(''));
        this.getGradeEditorSelectWidget().updateBody({
            description: this.gradeEditorRegistryItemRecord.get('description'),
            isMissingConfig: this._isMissingGradeEditorConfig()
        });
    }
});
