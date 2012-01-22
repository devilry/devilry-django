Ext.application({
    name: 'subjectadmingui',
    appFolder: window.DevilrySettings.DEVILRY_STATIC_URL + '/subjectadmingui/app',

    controllers: [
        'Actions'
    ],

    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: 'fit',
            items: {
                xtype: 'actionlist',
                links: [{
                    url: 'http://example.com',
                    label: 'Create new ...'
                }]
            }
        });
    }
});
