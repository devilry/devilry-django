Ext.application({
    name: 'subjectadmingui',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/subjectadmingui/app',

    controllers: [
        'ShortcutsTestMoch',
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
