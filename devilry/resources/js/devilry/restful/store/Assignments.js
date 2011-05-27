Ext.define('devilry.restful.store.Assignments', {
    extend: 'Ext.data.Store',
    requires: ['devilry.restful.model.Assignment'],
    model: 'devilry.restful.model.Assignment',
    autoLoad: true,
    autoSync: true,
    
    config: {
        longnamefields: 0
    },

    constructor: function(config) {
        this.initConfig(config);

        this.proxy = {
            type: 'rest',
            url: '/restful/examiner/assignments/',
            extraParams: {longnamefields:this.longnamefields},
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
