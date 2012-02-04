/**
 * Mixin for controllers that need to load an assignment from {@link
 * subjectadmin.store.SingleAssignment}.
 *
 * Requirements for the class using the mixin:
 *
 * - Methods to get the short names: ``getSubjectShortname()``,
 *   ``getPeriodShortname()``, ``getAssignmentShortname()``
 * - ``getMaskElement()`` method to get an element that is masked with the
 *   error message on failure.
 * - Implement ``onLoadAssignmentSuccess()``
 *
 * Example
 * =======
 *
 *     Ext.define('subjectadmin.controller.assignment.Overview', {
 *         mixins: {
 *             'loadAssignment': 'subjectadmin.utils.LoadAssignmentMixin'
 *         },
 *     
 *         _onRender: function() {
 *             ...
 *             this.loadAssignment();
 *         },
 *     
 *         getSubjectShortname: function() { ... },
 *         getPeriodShortname: function() { ... },
 *         getAssignmentShortname: function() { ... },
 *         getMaskElement: function() {
 *             return this.getSomething().getEl();
 *         },
 *         onLoadAssignmentSuccess: function(record) { ... },
 *     });
 */
Ext.define('subjectadmin.utils.LoadAssignmentMixin', {
    /** Load assignment.
     * Calls ``this.onLoadAssignmentSuccess(record)`` on success, and shows an
     * error on the ``this.getMaskElement()`` element on error.
     * */
    loadAssignment: function() {
        var store = this.getSingleAssignmentStore();
        store.loadAssignment(
            this.subject_shortname, this.period_shortname, this.assignment_shortname,
            this._onLoadAssignment, this
        );
    },

    _onLoadAssignment: function(records, operation) {
        if(operation.success) {
            this.onLoadAssignmentSuccess(records[0]);
        } else {
            this._onLoadAssignmentFailure(operation);
        }
    },

    _onLoadAssignmentFailure: function(operation) {
        var tpl = Ext.create('Ext.XTemplate',
            '<h2>{title}</h2>',
            '<p>{subject_shortname}.{period_shortname}.{assignment_shortname}</p>'
        );
        Ext.defer(function() { // NOTE: The delay is required for the mask to draw itself correctly.
            this.getMaskElement().mask(tpl.apply({
                title: dtranslate('themebase.doesnotexist'),
                subject_shortname: this.getSubjectShortname(),
                period_shortname: this.getPeriodShortname(),
                assignment_shortname: this.getAssignmentShortname()
            }), 'messagemask');
        }, 50, this);
    }
});
