/**
 * Mixin for controllers that need to load a Period.
 *
 * Requirements for the class using the mixin:
 *
 * - The ``Period`` model in models.
 * - Implement ``onLoadPeriodSuccess()``
 * - Implement ``onLoadPeriodFailure()``
 */
Ext.define('devilry_subjectadmin.utils.LoadPeriodMixin', {
    loadPeriod: function(subject_id) {
        this.getPeriodModel().load(subject_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this.onLoadPeriodSuccess(record);
                } else {
                    this.onLoadPeriodFailure(operation);
                }
            }
        });
    },
});
