/** Base class for windows used to Edit/Create SimplifiedRestful models. */
Ext.define('devilry.extjshelpers.SimplifiedRestfulEditWindowBase', {
    extend: 'Ext.window.Window',
    width: 800,
    height: 600,
    layout: 'fit',
    maximizable: true,
    modal: true,

    config: {
        /**
         * @cfg
         * The {@link devilry.extjshelpers.SimplifiedRestfulEditPanel} to use for editing.
         */
        editpanel: undefined
    },
    
    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },
    
    initComponent: function() {
        var me = this;
        this.editpanel.addListener('saveSucess', function(record) {
            me.onSaveSuccess(record);
        });

        Ext.apply(this, {
            items: this.editpanel
        });
        this.callParent(arguments);
    },

    onSaveSuccess: function(record) {
        throw "Must implement onSaveSuccess()"
    }
});
