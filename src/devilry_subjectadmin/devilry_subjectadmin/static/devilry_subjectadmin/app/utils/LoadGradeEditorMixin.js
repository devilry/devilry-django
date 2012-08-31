/**
 * Mixin for controllers that need to load the grade editor.
 *
 * Requirements for the class using the mixin:
 *
 * - 'GradeEditorConfig' and 'GradeEditorRegistryItem' in models.
 * - Implement:
 *      - onLoadGradeEditorConfigFailure(operation)
 *      - onLoadGradeEditorRegistryItemFailure(operation)
 *      - onLoadGradeEditorSuccess(gradeEditorConfigRecord, gradeEditorRegistryItemRecord)
 *
 * Example
 * =======
 *
 *     Ext.define('devilry_subjectadmin.controller.assignment.Overview', {
 *         mixins: ['devilry_subjectadmin.utils.LoadGradeEditorMixin'],
 *         models: [
 *            'GradeEditorConfig',
 *            'GradeEditorRegistryItem'
 *         ],
 *         _onRender: function() {
 *             ...
 *             this.loadGradeEditorRecords(assignment_id);
 *         },
 *     
 *         onLoadGradeEditorSuccess: function(record) { ... },
 *         onLoadGradeEditorConfigFailure: function(operation) { ... },
 *         onLoadGradeEditorRegistryItemFailure: function(operation) { ... },
 *     });
 */
Ext.define('devilry_subjectadmin.utils.LoadGradeEditorMixin', {

    /** Load grade editor config and registry item, and calls one of onLoadGradeEditorSuccess */
    loadGradeEditorRecords: function(assignment_id) {
        this.getGradeEditorConfigModel().load(assignment_id, {
            scope: this,
            success: this._loadGradeEditorRegistryItem,
            failure: function(unused, operation) {
                this.onLoadGradeEditorConfigFailure(operation);
            }
        });
    },

    _loadGradeEditorRegistryItem: function(gradeEditorConfigRecord) {
        var gradeeditorid = gradeEditorConfigRecord.get('gradeeditorid');
        this.getGradeEditorRegistryItemModel().load(gradeeditorid, {
            scope: this,
            success: function(gradeEditorRegistryItemRecord) {
                this.onLoadGradeEditorSuccess(gradeEditorConfigRecord,
                    gradeEditorRegistryItemRecord);
            },
            failure: function(unused, operation) {
                this.onLoadGradeEditorRegistryItemFailure(operation);
            }
        });
    }
});
