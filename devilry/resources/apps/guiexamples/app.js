Ext.application({
    name: 'guiexamples',

    appFolder: '/resources/addons/guiexamples/app',

    controllers: [
        'Users'
    ],

    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: 'fit',
            items: [
                {
                    xtype: 'userlist',
                }
            ]
        });
    }
});
