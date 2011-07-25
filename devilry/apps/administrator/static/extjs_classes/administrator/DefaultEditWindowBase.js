/** Base class for the default config for the Edit/Create new window, which is
 * opened to edit/create new item in the admin interface. */
Ext.define('devilry.administrator.DefaultEditWindowBase', {
    extend: 'Ext.window.Window',
    width: 800,
    height: 600,
    layout: 'fit',
    maximizable: true,

    config: {
        /**
         * @cfg
         * The {@link devilry.administrator.EditPanel} to use for editing.
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
