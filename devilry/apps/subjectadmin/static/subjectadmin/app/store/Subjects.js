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
    }
});
