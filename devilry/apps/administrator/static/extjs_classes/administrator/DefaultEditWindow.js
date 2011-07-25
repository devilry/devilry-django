/** Default config for the Edit window, which is opened to edit an item in the
 * admin interface. */
Ext.define('devilry.administrator.DefaultEditWindow', {
    extend: 'devilry.administrator.DefaultEditWindowBase',
    title: 'Edit',
    
    config: {
        /**
         * @cfg
         * The {@link devilry.administrator.PrettyView} to refresh when a save succeeds.
         */
        prettyview: undefined
    },

    onSaveSuccess: function(record) {
        this.prettyview.setRecord(record);
        this.close();
    }
});
