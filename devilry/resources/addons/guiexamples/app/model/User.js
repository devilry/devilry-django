Ext.define('guiexamples.model.User', {
    extend: 'Ext.data.Model',
    fields: ['username', 'email'],
    idProperty: 'username',

    proxy: {
        type: 'rest',
        url: '/guiexamples/all-users/',
        //api: {
            //read: '/guiexamples/all-users',
            //update: '/guiexamples/update-users'
        //},
        reader: {
            type: 'json',
            root: 'users',
            //successProperty: 'success'
        },
        writer: 'json'
    }
});
