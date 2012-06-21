/**
 * Mixin for controllers that need to load a Subject.
 *
 * Requirements for the class using the mixin:
 *
 * - The ``Subject`` model in models.
 * - Implement ``onLoadSubjectSuccess()``
 * - Implement ``onLoadSubjectFailure()``
 */
Ext.define('devilry_subjectadmin.utils.LoadSubjectMixin', {
    loadSubject: function(subject_id) {
        this.getSubjectModel().load(subject_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this.onLoadSubjectSuccess(record);
                } else {
                    this.onLoadSubjectFailure(operation);
                }
            }
        });
    },
});
