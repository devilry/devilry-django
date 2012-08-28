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
        ref: 'gradeEditorSelectCombobox',
        selector: 'gradeeditorselectwindow gradeeditorselector'
    }, {
        ref: 'gradeEditorSelectSaveButton',
        selector: 'gradeeditorselectwindow savebutton'
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
                click: this._onSaveGradeEditorSelection
            },
            'gradeeditorselectwindow cancelbutton': {
                click: this._closeSelectWindow
            },
            'gradeeditorselectwindow gradeeditorselector': {
                change: this._onGradeEditorSelectorChange
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

    _onLoadGradeEditorConfigSuccess: function(gradeEditorConfigRecord) {
        this.gradeEditorConfigRecord = gradeEditorConfigRecord;
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
        Ext.widget('gradeeditorselectwindow', {
            gradeeditorid: this.gradeEditorConfigRecord.get('gradeeditorid')
        }).show();
    },

    _closeSelectWindow: function() {
        this.getGradeEditorSelectWindow().close();
    },

    _onSaveGradeEditorSelection: function() {
        this.getGradeEditorSelectWindow().setLoading('Saving') + ' ...';
        var combobox = this.getGradeEditorSelectCombobox();
        var value = combobox.getValue();
        this.gradeEditorConfigRecord.set('gradeeditorid', value);
        this.gradeEditorConfigRecord.set('config', '');
        this.gradeEditorConfigRecord.save({
            scope: this,
            success: this._onSaveGradeEditorConfigSuccess,
            failure: function(unused, op) {
                console.log('save error', op);
            }
        });
    },

    _onSaveGradeEditorConfigSuccess: function(gradeEditorConfigRecord) {
        console.log('GradeEditorConfig saved', gradeEditorConfigRecord);
        this.getGradeEditorSelectWindow().close();
        this._onLoadGradeEditorConfigSuccess(gradeEditorConfigRecord);
    },

    _onGradeEditorSelectorChange: function(combo, newValue) {
        var currentValue = this.gradeEditorConfigRecord.get('gradeeditorid');
        console.log('change', currentValue, newValue);
        if(newValue !== currentValue) {
            this.getGradeEditorSelectSaveButton().enable();
        } else {
            this.getGradeEditorSelectSaveButton().disable();
        }
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
        var title, body;
        this.getGradeEditorSelectWidget().updateTitle(gettext('Grade editor'));
        var config_editor_url = this.gradeEditorRegistryItemRecord.get('config_editor_url');
        this.getGradeEditorSelectWidget().updateBody({
            title: this.gradeEditorRegistryItemRecord.get('title'),
            //description: this.gradeEditorRegistryItemRecord.get('description'),
            isMissingConfig: this._isMissingGradeEditorConfig(),
            configurable: !Ext.isEmpty(config_editor_url)
        });
    }
});
