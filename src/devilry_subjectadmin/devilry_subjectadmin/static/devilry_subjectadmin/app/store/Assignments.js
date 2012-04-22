/**
 * Used by the {@link devilry_subjectadmin.controller.Assignment} controller to load
 * a single assignment into its view. We need a store because we use a query.
 */
Ext.define('devilry_subjectadmin.store.Assignments', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.Assignment',

    loadAssignment: function(subject_shortname, period_shortname, assignment_shortname, callbackFn, callbackScope) {
        this.proxy.extraParams.exact_number_of_results = 1;
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
