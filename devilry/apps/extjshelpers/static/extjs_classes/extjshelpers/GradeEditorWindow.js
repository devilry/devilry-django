Ext.define('devilry.extjshelpers.GradeEditorWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.gradeeditor',
    title: 'Create feedback',
    width: 800,
    height: 600,
    layout: 'fit',

    config: {
        /**
         * @cfg
         * ID of the Delivery where the feedback belongs.
         */
        deliveryid: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    /**
     * Exit the grade editor.
     */
    exit: function() {
        this.close();
    }
});
