Ext.application({
    name: 'subjectadmingui',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/subjectadmingui/app',

    controllers: [
        'Actions',
        'Shortcuts'
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
