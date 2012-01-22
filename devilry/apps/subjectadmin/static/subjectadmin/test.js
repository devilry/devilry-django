Ext.application({
    name: 'subjectadmin',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/subjectadmin/app',

    controllers: [
        'ShortcutsTestMock',
    ],

    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: 'fit',
            items: {
                xtype: 'shortcutlist'
            }
        });
    }
});
