Ext.define('devilry_subjectadmin.store.Assignments', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.Assignment',

    loadAssignmentsInPeriod: function(period_id, callbackFn, callbackScope) {
        this.proxy.extraParams.parentnode = period_id;
        this.load({
            scope: callbackScope,
            callback: callbackFn
        });
    }
});
