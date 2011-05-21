Ext.define('guiexamples.store.Users', {
    extend: 'Ext.data.Store',
    model: 'guiexamples.model.User',
    data: [
        {name: 'Ed',    email: 'ed@sencha.com'},
        {name: 'Tommy', email: 'tommy@sencha.com'}
    ]
});
