Ext.define('devilry_subjectadmin.controller.GradeEditor', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin',
        'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.LoadGradeEditorMixin'
    ],

    requires: [
        'devilry.gradeeditors.ConfigEditorWidget'
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
        var title = gettext('Grade editor');
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
        if(this.gradeEditorRegistryItemRecord.isConfigurable()) {
            this._addConfigWidget();
        }
        console.log(this.gradeEditorConfigRecord.data);
        console.log(this.gradeEditorRegistryItemRecord.data);
    },

    _addConfigWidget: function() {
        var currentConfigEditor = this.getGradeConfigEditor();
        if(currentConfigEditor) {
            currentConfigEditor.remove();
        }
        this.getOverview().add({
            xtype: 'gradeconfigeditor',
            registryitem: this.gradeEditorRegistryItemRecord.data,
            gradeEditorConfigRecord: this.gradeEditorConfigRecord,
            listeners: {
                scope: this,
                saveSuccess: function(configeditor, gradeEditorConfigRecord) {
                    console.log('Saved', gradeEditorConfigRecord);
                }
            }
        });
    }
});
