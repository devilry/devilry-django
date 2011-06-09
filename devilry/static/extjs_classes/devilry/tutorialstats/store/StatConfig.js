Ext.define('devilry.tutorialstats.store.StatConfig', {
    extend: 'Ext.data.Store',
    requires: ['devilry.tutorialstats.model.StatConfig'],
    model: 'devilry.tutorialstats.model.StatConfig',
    autoLoad: true,
    autoSync: true,
    
    constructor: function(config) {
        this.initConfig(config);

        this.proxy = {
            type: 'rest',
            url: '/tutorialstats/rest/',
            reader: {
                type: 'json',
                root: 'items'
            },
            writer: 'json'
        };

        this.callParent([config]);
        return this;
    },
});
