Ext.define('devilry.student.stores.UploadedFileStore', {
    extend: 'Ext.data.ArrayStore',

    // Store configs
    autoDestroy: true,

    // Reader configs
    idIndex: 0,
    fields:[
        {name: 'filename', type: 'string'}
    ]
});
