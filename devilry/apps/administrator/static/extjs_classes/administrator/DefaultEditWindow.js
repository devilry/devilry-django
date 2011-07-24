/** Default config for the Edit window, which is opened to edit an item and the
 * admin interface. */
Ext.define('devilry.administrator.DefaultEditWindow', {
    extend: 'Ext.window.Window',
    title: 'Edit',
    width: 800,
    height: 600,
    layout: 'fit',
    maximizable: true,
    
    config: {
        /**
         * @cfg
         * The {@link devilry.administrator.EditPanel} to use for editing.
         */
        editpanel: undefined,

        /**
         * @cfg
         * The {@link devilry.administrator.PrettyView} to refresh when a save succeeds.
         */
        prettyview: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },
    
    initComponent: function() {
        var me = this;
        this.editpanel.addListener('saveSucess', function(record) {
            me.close();
            me.prettyview.setRecord(record);
        });

        Ext.apply(this, {
            items: this.editpanel
        });
        this.callParent(arguments);
    }
});
