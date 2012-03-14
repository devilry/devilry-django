Ext.define('subjectadmin.store.Subjects', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.Subject',

    loadSubject: function(subject_shortname, callbackFn, callbackScope) {
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
        this.proxy.setDevilryFilters([]);
        this.load(config);
    }
});
