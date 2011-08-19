Ext.define('devilry.asminimalaspossible_gradeeditor.DummyWindow', {
    extend: 'Ext.window.Window',

    width: 200,
    height: 200,
    modal: true,
    layout: 'fit',

    config: {
        /**
         * @cfg
         * A message to show. (required)
         */
        message: undefined,

        /**
         * @cfg
         * Label of the toolbar button. (required)
         */
        buttonLabel: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'panel',
                html: this.message
            }],
            
            bbar: [{
                xtype: 'button',
                text: this.buttonLabel
            }]
        });
        this.callParent(arguments);
    }
});
