Ext.define('devilry_subjectadmin.controller.GradeEditor', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin',
        'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.LoadGradeEditorMixin'
    ],

    requires: [
        'devilry.gradeeditors.ConfigEditorWidget',
        'devilry_extjsextras.SaveButton',
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    views: [
        'gradeeditor.Overview'
    ],

    models: [
        'Assignment',
        'GradeEditorConfig',
        'GradeEditorRegistryItem'
    ],

    stores: [
        'GradeEditors'
    ],

    refs: [{
        ref: 'overview',
        selector: 'gradeeditoroverview'
    }, {
        ref: 'globalAlertmessagelist',
        selector: 'gradeeditoroverview #globalAlertmessagelist'
    }, {
        ref: 'gradeEditorEdit',
        selector: 'gradeeditoroverview gradeeditoredit'
    }, {
        ref: 'about',
        selector: 'gradeeditoroverview gradeeditoredit #about'
    }, {
        ref: 'configContainer',
        selector: 'gradeeditoroverview gradeeditoredit #configContainer'
    }, {
        ref: 'noConfigBody',
        selector: 'gradeeditoroverview gradeeditoredit #noConfigBody'
    }, {
        ref: 'gradeConfigEditor',
        selector: 'gradeeditoroverview gradeeditoredit gradeconfigeditor'
    }, {
        ref: 'gradeEditorChange',
        selector: 'gradeeditoroverview gradeeditorchange'
    }, {
        ref: 'gradeEditorChooseGrid',
        selector: 'gradeeditoroverview gradeeditorchange gradeeditorchoosegrid'
    }, {
        ref: 'clearConfigConfirmContainer',
        selector: 'viewport gradeeditoroverview gradeeditorchange #clearConfigConfirmContainer'
    }, {
        ref: 'clearConfigConfirmCheckbox',
        selector: 'viewport gradeeditoroverview gradeeditorchange #clearConfigConfirmCheckbox'
    }, {
        ref: 'gradeEditorChangeSaveButton',
        selector: 'gradeeditoroverview gradeeditorchange savebutton'
    }],

    init: function() {
        this.control({
            'viewport gradeeditoroverview #about': {
                render: this._onRender
            },
            'viewport gradeeditoroverview gradeeditorchange gradeeditorchoosegrid': {
                selectionchange: this._onGradeEditorSelectionChange
            },
            'viewport gradeeditoroverview gradeeditorchange #clearConfigConfirmCheckbox': {
                change: this._onGradeEditorSelectionChange
            },
            'viewport gradeeditoroverview gradeeditorchange savebutton': {
                click: this._onSaveGradeEditorSelection
            },
            'viewport gradeeditoroverview gradeeditorchange #cancelButton': {
                click: this._onCancelGradeEditorSelection
            }
        });
    },

    _setLoading: function() {
        this.getOverview().setLoading(gettext('Loading') + ' ...');
    },
    _setNotLoading: function() {
        this.getOverview().setLoading(false);
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        this._setLoading();
        this.assignment_id = this.getOverview().assignment_id;
        this.loadAssignment(this.assignment_id);
    },

    _setBreadcrumb: function(change) {
        var title = gettext('Grade editor');
        if(change) {
            this.setSubviewBreadcrumb(this.assignmentRecord, 'Assignment', [{
                text: title,
                url: devilry_subjectadmin.utils.UrlLookup.editGradeEditor(
                    this.assignmentRecord.get('id'))
            }], gettext('Change'));
        } else {
            this.setSubviewBreadcrumb(this.assignmentRecord, 'Assignment', [], title);
        }
    },


    //
    //
    // Load
    //
    //
    onLoadAssignmentSuccess: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this._setBreadcrumb();
        this._setNotLoading();
        this._loadAllExceptAssignment();
    },
    onLoadAssignmentFailure: function(operation) {
        this._setNotLoading();
        this.onLoadFailure(operation);
    },

    _loadAllExceptAssignment: function() {
        this._setLoading();
        this.loadGradeEditorRecords(this.assignmentRecord.get('id'));
    },

    onLoadGradeEditorSuccess: function(gradeEditorConfigRecord, gradeEditorRegistryItemRecord) {
        this._setNotLoading();
        this.gradeEditorConfigRecord = gradeEditorConfigRecord;
        this.gradeEditorRegistryItemRecord = gradeEditorRegistryItemRecord;
        this._onAllLoaded();
    },
    onLoadGradeEditorConfigFailure: function(operation) {
        this._setNotLoading();
        console.error(operation);
    },
    onLoadGradeEditorRegistryItemFailure: function(operation) {
        this._setNotLoading();
        console.error(operation);
    },

    _onAllLoaded: function() {
        var changeGradeEditor = this.getOverview().changeGradeEditor;
        if(changeGradeEditor) {
            this._showChangeGradeEditor();
            return;
        } 
        else {
            this._setupAboutBox();
            if(this.gradeEditorRegistryItemRecord.isConfigurable()) {
                this._addConfigWidget();
            } else {
                this._setupNoConfigBody();
            }
        }
    },
    _setupAboutBox: function() {
        this.getAbout().update({
            registryitem: this.gradeEditorRegistryItemRecord.data,
            changeurl: this._getChangeGradeEditorHash()
        });
    },
    _setupNoConfigBody: function() {
        this.getNoConfigBody().update({
            assignmentname: this.assignmentRecord.get('short_name'),
            assignmenthash: this._getAssignmentHash()
        });
    },
    _getAssignmentHash: function() {
        return devilry_subjectadmin.utils.UrlLookup.assignmentOverview(this.assignmentRecord.get('id'));
    },
    _getChangeGradeEditorHash: function() {
        return devilry_subjectadmin.utils.UrlLookup.changeGradeEditor(this.assignmentRecord.get('id'));
    },


    //
    //
    // Config editor
    //
    //

    _isMissingGradeEditorConfig: function() {
        var config = this.gradeEditorConfigRecord.get('config');
        return Ext.isEmpty(config) && this.gradeEditorRegistryItemRecord.isConfigurable();
    },

    _addConfigWidget: function() {
        this.getConfigContainer().removeAll();
        this.getConfigContainer().add([{
            xtype: 'box',
            cls: 'bootstrap',
            tpl: [
                '<h2>',
                    gettext('Configure grade editor'),
                '</h2>',
                '<tpl if="isMissingConfig">',
                    '<div class="alert alert-warning missing_config">',
                            gettext('This grade editor requires configuration. Examiners can not provide feedback to students until you have provided configuration. Use the form below to configure the grade editor.'),
                    '</div>',
                '<tpl else>',
                    '<p><small>',
                        gettext('This grade editor requires configuration, and configuration has already been provided by you or another administrator. Use the form below if you wish to change the configuration.'),
                    '</small></p>',
                '</tpl>',
                '</div>'
            ],
            data: {
                isMissingConfig: this._isMissingGradeEditorConfig()
            }
        }, {
            xtype: 'panel',
            //border: false,
            bodyPadding: 10,
            items: [{
                xtype: 'gradeconfigeditor',
                registryitem: this.gradeEditorRegistryItemRecord.data,
                gradeEditorConfigRecord: this.gradeEditorConfigRecord,
                listeners: {
                    scope: this,
                    saveSuccess: this._onSaveConfigSuccess,
                    saveFailed: this._onSaveConfigFailure
                }
            }],
            dockedItems: [{
                dock: 'bottom',
                xtype: 'toolbar',
                ui: 'footer',
                items: [{
                    xtype: 'button',
                    text: gettext('Cancel'),
                    listeners: {
                        scope: this,
                        click: this._onCancelEditConfig
                    }
                }, '->', {
                    xtype: 'button',
                    text: gettext('Save and continue editing'),
                    listeners: {
                        scope: this,
                        click: this._onSaveConfigAndContinueEditing
                    }
                }, {
                    xtype: 'savebutton',
                    listeners: {
                        scope: this,
                        click: this._onSaveConfig
                    }
                }]
            }]
        }]);
    },

    _onCancelEditConfig: function() {
        this.application.route.navigate(this._getAssignmentHash());
    },

    _onSaveConfigAndContinueEditing: function() {
        this._continueEditAfterSave = true;
        this._onSaveConfig();
    },
    _onSaveConfig: function() {
        this.getConfigContainer().setLoading(gettext('Saving') + ' ...');
        this.getGradeConfigEditor().triggerSave();
    },

    _onSaveConfigSuccess: function(configeditor, gradeEditorConfigRecord) {
        this.getConfigContainer().setLoading(false);
        if(this._continueEditAfterSave) {
            this._loadAllExceptAssignment();
        } else {
            this.application.route.navigate(this._getAssignmentHash());
        }
        this._continueEditAfterSave = undefined;
    },
    _onSaveConfigFailure: function(configeditor, gradeEditorConfigRecord) {
        this.getConfigContainer().setLoading(false);
        // NOTE: Showing errors is handled by the ConfigEditorWidget itself.
    },



    //
    //
    // Change grade editor
    //
    //

    _showChangeGradeEditor: function() {
        this.getGradeEditorEdit().hide();
        this.getGradeEditorChange().show();
        this._setBreadcrumb(true);
        this.getGradeEditorsStore().load({
            scope: this,
            callback: function(records, operation) {
                if(operation.success) {
                    this._onLoadGradeEditorsStoreSuccess(records);
                } else {
                    this._onLoadGradeEditorsStoreFailure(operation);
                }
            }
        });
    },
    _onLoadGradeEditorsStoreSuccess: function(records) {
        var store = this.getGradeEditorsStore();
        store.sort('title', 'ASC');
        var index = store.findExact('gradeeditorid', this.gradeEditorConfigRecord.get('gradeeditorid'));
        if(index > -1) {
            var selModel = this.getGradeEditorChooseGrid().getSelectionModel();
            var record = store.getAt(index);
            selModel.select([record]);
        }
    },
    _onLoadGradeEditorsStoreFailure: function(operation) {
        console.error(operation);
    },

    _onGradeEditorSelectionChange: function() {
        var selModel = this.getGradeEditorChooseGrid().getSelectionModel();
        var newValue = selModel.getSelection()[0].get('gradeeditorid');
        var currentValue = this.gradeEditorConfigRecord.get('gradeeditorid');
        var saveButton = this.getGradeEditorChangeSaveButton();
        if(newValue !== currentValue) {
            var isConfigurable = this.gradeEditorRegistryItemRecord.isConfigurable();
            var hasConfig = this.gradeEditorConfigRecord.hasConfig();
            if(isConfigurable && hasConfig) {
                var clearConfirmed = this.getClearConfigConfirmCheckbox().getValue();
                if(isConfigurable && hasConfig && clearConfirmed) {
                    saveButton.enable();
                    return;
                } else {
                    this.getClearConfigConfirmContainer().show();
                }
            } else {
                saveButton.enable();
                return;
            }
        }
        saveButton.disable();
    },

    _onSaveGradeEditorSelection: function() {
        this._saveGradeEditorSelection();
    },
    _saveGradeEditorSelection: function() {
        var selModel = this.getGradeEditorChooseGrid().getSelectionModel();
        var selected = selModel.getSelection()[0];
        this.getGradeEditorChange().setLoading(gettext('Saving') + ' ...');
        var gradeeditorid = selected.get('gradeeditorid');
        this.gradeEditorConfigRecord.set('gradeeditorid', gradeeditorid);
        this.gradeEditorConfigRecord.set('config', '');
        this.gradeEditorConfigRecord.save({
            scope: this,
            success: this._onSaveGradeEditorConfigSuccess,
            failure: this._onSaveGradeEditorConfigFailure
        });
    },
    _onSaveGradeEditorConfigSuccess: function(gradeEditorConfigRecord) {
        this.getGradeEditorChange().setLoading(false);
        this._navigateToEditView();
    },
    _onSaveGradeEditorConfigFailure: function(unused, operation) {
        console.error(operation);
    },

    _onCancelGradeEditorSelection: function() {
        this._navigateToEditView();
    },

    _navigateToEditView: function() {
        this.application.route.navigate(
            devilry_subjectadmin.utils.UrlLookup.editGradeEditor(
                this.assignmentRecord.get('id')));
    }
});
