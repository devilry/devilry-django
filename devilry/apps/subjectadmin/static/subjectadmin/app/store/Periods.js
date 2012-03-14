Ext.define('subjectadmin.store.Periods', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.Period',

    loadPeriod: function(subject_shortname, period_shortname, callbackFn, callbackScope) {
        this.proxy.setDevilryFilters([
            {field:"parentnode__short_name", comp:"exact", value:subject_shortname},
            {field:"short_name", comp:"exact", value:period_shortname}
        ]);
        this.load({
            scope: callbackScope,
            callback: callbackFn
        });
    },

    loadPeriodsInSubject: function(subject_shortname, callbackFn, callbackScope) {
        this.proxy.extraParams.limit = 100000;
        this.proxy.setDevilryFilters([]);
        this.load({
            scope: callbackScope,
            callback: callbackFn
        });
    }
});
