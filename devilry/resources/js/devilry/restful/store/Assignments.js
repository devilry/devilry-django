Ext.define('devilry.restful.store.Assignments', {
    extend: 'Ext.data.Store',
    model: 'devilry.restful.model.Assignment',
    //storeId: 'AssignmentsStore',
    autoLoad: true,
    autoSync: true,

    proxy: {
        type: 'rest',
        url: '/restful/examiner/assignments/',
        reader: {
            type: 'json',
        },
        writer: 'json'
    }
});
