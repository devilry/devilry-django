Ext.define('subjectadmin.store.Subjects', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.Subject',

    loadSubject: function(subject_shortname, callbackFn, callbackScope) {
        this.proxy.extraParams.exact_number_of_results = 1;
        this.proxy.setDevilryFilters([
            {field:"short_name", comp:"exact", value:subject_shortname}
        ]);
        this.load({
            scope: callbackScope,
            callback: callbackFn
        });
    },

    loadAll: function(config) {
        this.proxy.extraParams.limit = 100000;
        this.proxy.extraParams.exact_number_of_results = undefined;
        this.proxy.setDevilryFilters([]);
        this.load(config);
    }
});
