Ext.define('guiexamples.model.User', {
    extend: 'Ext.data.Model',
    fields: ['username', 'email'],

    proxy: {
        type: 'ajax',
        api: {
            read: '/guiexamples/all-users',
            update: '/guiexamples/update-users'
        },
        reader: {
            type: 'json',
            root: 'users',
            successProperty: 'success'
        }
    }
});
