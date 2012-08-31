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
        'devilry_extjsextras.SaveButton'
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
            'viewport gradeeditoroverview #globalAlertmessagelist': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        this.getOverview().setLoading(gettext('Loading') + ' ...');
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
        this.loadGradeEditorRecords(assignmentRecord.get('id'));
    },
    onLoadAssignmentFailure: function(operation) {
        this.onLoadFailure(operation);
    },

    onLoadGradeEditorSuccess: function(gradeEditorConfigRecord, gradeEditorRegistryItemRecord) {
        this.getOverview().setLoading(false);
        this.gradeEditorConfigRecord = gradeEditorConfigRecord;
        this.gradeEditorRegistryItemRecord = gradeEditorRegistryItemRecord;
        console.log(this.gradeEditorConfigRecord.data);
        console.log(this.gradeEditorRegistryItemRecord.data);

        this.getAbout().update({
            registryitem: this.gradeEditorRegistryItemRecord.data
        });
        if(this.gradeEditorRegistryItemRecord.isConfigurable()) {
            this._addConfigWidget();
        }
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
        console.log('Saved', gradeEditorConfigRecord);
    },
    _onSaveConfigFailure: function(configeditor, gradeEditorConfigRecord) {
        this.getConfigContainer().setLoading(false);
        // NOTE: Showing errors is handled by the ConfigEditorWidget itself.
    }
});
