Ext.define('devilry_qualifiesforexam_select.store.AggregatedRelatedStudentInfos', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.AggregatedRelatedStudentInfo',

    autoLoad: true,
    proxy: {
        type: 'memory'
    }
});
