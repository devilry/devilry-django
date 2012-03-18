/**
 * Used by the {@link subjectadmin.controller.Assignment} controller to load
 * a single assignment into its view. We need a store because we use a query.
 */
Ext.define('subjectadmin.store.SingleAssignment', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.Assignment',

    loadAssignment: function(subject_shortname, period_shortname, assignment_shortname, callbackFn, callbackScope) {
        this.proxy.setDevilryFilters([
            {field:"parentnode__parentnode__short_name", comp:"exact", value:subject_shortname},
            {field:"parentnode__short_name", comp:"exact", value:period_shortname},
            {field:"short_name", comp:"exact", value:assignment_shortname}
        ]);
        this.load({
            scope: callbackScope,
            callback: callbackFn
        });
    },

    loadAssignmentsInPeriod: function(subject_shortname, period_shortname, callbackFn, callbackScope) {
        this.proxy.extraParams.limit = 100000;
        this.proxy.setDevilryFilters([
            {field:"parentnode__parentnode__short_name", comp:"exact", value:subject_shortname},
            {field:"parentnode__short_name", comp:"exact", value:period_shortname},
        ]);
        this.load({
            scope: callbackScope,
            callback: callbackFn
        });
    }
});
