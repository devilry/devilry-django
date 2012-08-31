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
        ref: 'gradeConfigEditor',
        selector: 'gradeeditoroverview gradeeditoredit gradeconfigeditor'
    }, {
        ref: 'gradeEditorChange',
        selector: 'gradeeditoroverview gradeeditorchange'
    }, {
        ref: 'gradeEditorChooseGrid',
        selector: 'gradeeditoroverview gradeeditorchange gradeeditorchoosegrid'
    }],

    init: function() {
        this.control({
            'viewport gradeeditoroverview #about': {
                render: this._onRender
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
        this.getAbout().addListener({
            scope: this,
            element: 'el',
            delegate: 'a',
            click: function(e) {
                this._onChangeGradeEditor();
                e.preventDefault();
            }
        });
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
            }
        }
    },

    _setupAboutBox: function() {
        this.getAbout().update({
            registryitem: this.gradeEditorRegistryItemRecord.data
        });
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
                    '<div class="alert alert-warning">',
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
                items: ['->', {
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
            this.application.route.navigate(
                devilry_subjectadmin.utils.UrlLookup.assignmentOverview(
                    this.assignmentRecord.get('id')));
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

    _onChangeGradeEditor: function() {
        this.application.route.navigate(
            devilry_subjectadmin.utils.UrlLookup.changeGradeEditor(
                this.assignmentRecord.get('id')));
    },

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

    _onSaveGradeEditorSelection: function() {
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
