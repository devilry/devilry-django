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

    refs: [{
        ref: 'overview',
        selector: 'gradeeditoroverview'
    }, {
        ref: 'globalAlertmessagelist',
        selector: 'gradeeditoroverview #globalAlertmessagelist'
    }, {
        ref: 'about',
        selector: 'gradeeditoroverview #about'
    }, {
        ref: 'configContainer',
        selector: 'gradeeditoroverview #configContainer'
    }, {
        ref: 'gradeConfigEditor',
        selector: 'gradeeditoroverview gradeconfigeditor'
    }],

    init: function() {
        this.control({
            'viewport gradeeditoroverview #about': {
                render: this._onRender
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

    _setBreadcrumb: function(subviewtext) {
        var title = gettext('Edit grade editor');
        this.setSubviewBreadcrumb(this.assignmentRecord, 'Assignment', [], title);
    },
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

        this._setupAboutBox();
        if(this.gradeEditorRegistryItemRecord.isConfigurable()) {
            this._addConfigWidget();
        }
    },
    onLoadGradeEditorConfigFailure: function(operation) {
        this._setNotLoading();
        console.error(operation);
    },
    onLoadGradeEditorRegistryItemFailure: function(operation) {
        this._setNotLoading();
        console.error(operation);
    },

    _setupAboutBox: function() {
        this.getAbout().update({
            registryitem: this.gradeEditorRegistryItemRecord.data
        });
    },

    _isMissingGradeEditorConfig: function() {
        var config = this.gradeEditorConfigRecord.get('config');
        return Ext.isEmpty(config) && this._isConfigurable();
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
                    '<div class="alert alert-error">',
                            gettext('This grade editor requires configuration. Examiners can not provide feedback to students until you have provided configuration. Use the form below if to configure the grade editor.'),
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
        console.log('change');
    },
});
