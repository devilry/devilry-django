Ext.define('devilry_qualifiesforexam.store.AggregatedRelatedStudentInfosBase', {
    extend: 'Ext.data.Store',
    model: 'devilry_qualifiesforexam.model.AggregatedRelatedStudentInfo',

    autoLoad: true,
    proxy: {
        type: 'memory'
    }
});