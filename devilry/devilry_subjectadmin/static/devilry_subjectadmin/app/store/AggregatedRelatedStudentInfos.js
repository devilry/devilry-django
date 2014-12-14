Ext.define('devilry_subjectadmin.store.AggregatedRelatedStudentInfos', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.AggregatedRelatedStudentInfo',

    autoLoad: true,
    proxy: {
        type: 'memory'
    }
});