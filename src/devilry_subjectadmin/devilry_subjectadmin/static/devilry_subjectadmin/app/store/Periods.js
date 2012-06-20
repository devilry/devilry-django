Ext.define('devilry_subjectadmin.store.Periods', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.Period',

    loadPeriodsInSubject: function(subject_id, callbackFn, callbackScope) {
        this.proxy.extraParams.parentnode = subject_id;
        this.load({
            scope: callbackScope,
            callback: callbackFn
        });
    }
});
