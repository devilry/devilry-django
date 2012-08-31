Ext.define('devilry_subjectadmin.controller.assignment.EditGradeEditor', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.LoadGradeEditorMixin'
    ],

    requires: [
        'devilry.gradeeditors.ConfigEditorWidget',
        'Ext.window.MessageBox'
    ],

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
                edit: this._onEdit,
                bodyLinkClicked: this._onConfigureGradeEditor
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
        this.getGradeEditorSelectWindow().close();
        this._onLoadGradeEditorConfigSuccess(gradeEditorConfigRecord);
    },

    _onGradeEditorSelectorChange: function(combo, newValue) {
        var currentValue = this.gradeEditorConfigRecord.get('gradeeditorid');
        if(newValue !== currentValue) {
            this.getGradeEditorSelectSaveButton().enable();
        } else {
            this.getGradeEditorSelectSaveButton().disable();
        }
    },

    
    //
    //
    // Config editor window
    //
    //
    _onConfigureGradeEditor: function() {
        if(!this._isConfigurable()) {
            // NOTE: No translations because you do not get here through normal UI navigation.
            Ext.MessageBox.alert('Invalid action',
                Ext.String.format('"{0}" is not configurable.',
                    this.gradeEditorRegistryItemRecord.get('title'))
            );
            return;
        }
        Ext.widget('gradeconfigeditor', {
            registryitem: this.gradeEditorRegistryItemRecord.data,
            gradeEditorConfigRecord: this.gradeEditorConfigRecord,
            listeners: {
                scope: this,
                saveSuccess: function(win, gradeEditorConfigRecord) {
                    win.close();
                    this._onLoadGradeEditorConfigSuccess(gradeEditorConfigRecord)
                }
            }
        }).show();
    },


    //
    //
    // The widget
    //
    //

    _isConfigurable: function () {
        return this.gradeEditorRegistryItemRecord.isConfigurable();
    },

    _isMissingGradeEditorConfig: function() {
        return this.gradeEditorConfigRecord.hasConfig() && this._isConfigurable();
    },

    _updateWidget: function() {
        var title, body;
        this.getGradeEditorSelectWidget().updateTitle(gettext('Grade editor'));
        var config_editor_url = this.gradeEditorRegistryItemRecord.get('config_editor_url');
        this.getGradeEditorSelectWidget().updateBody({
            title: this.gradeEditorRegistryItemRecord.get('title'),
            //description: this.gradeEditorRegistryItemRecord.get('description'),
            isMissingConfig: this._isMissingGradeEditorConfig(),
            configurable: this._isConfigurable()
        });
    }
});
