/**
 * Mixin for controllers that need to load an assignment from
 * {@link devilry_subjectadmin.store.Assignments}.
 *
 * Requirements for the class using the mixin:
 *
 * - The ``Assignments`` store in stores.
 * - Methods to get the short names: ``getSubjectShortname()``,
 *   ``getPeriodShortname()``, ``getAssignmentShortname()``
 * - ``getMaskElement()`` method to get an element that is masked with the
 *   error message on failure.
 * - Implement ``onLoadAssignmentSuccess()``
 *
 * Example
 * =======
 *
 *     Ext.define('devilry_subjectadmin.controller.assignment.Overview', {
 *         mixins: {
 *             'loadAssignment': 'devilry_subjectadmin.utils.LoadAssignmentMixin'
 *         },
 *         models: [
 *             'Assignment'
 *         ],
 *         _onRender: function() {
 *             ...
 *             this.loadAssignment(assignment_id);
 *         },
 *     
 *         onLoadAssignmentSuccess: function(record) { ... },
 *         onLoadAssignmentFailure: function(operation) { ... },
 *     });
 */
Ext.define('devilry_subjectadmin.utils.LoadAssignmentMixin', {
    /** Load assignment.
     * Calls ``this.onLoadAssignmentSuccess(record)`` on success,
     * ``this.onLoadAssignmentFailure(operation) on failure.
     * */
    loadAssignment: function(assignment_id) {
        this.getAssignmentModel().load(assignment_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this.onLoadAssignmentSuccess(record);
                } else {
                    this.onLoadAssignmentFailure(operation);
                }
            }
        });
    }
});
