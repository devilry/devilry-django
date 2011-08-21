/** Base class for windows used to Edit/Create RestfulSimplified models. */
Ext.define('devilry.extjshelpers.RestfulSimplifiedEditWindowBase', {
    extend: 'devilry.extjshelpers.MaximizableWindow',
    //width: 800,
    //height: 600,
    layout: 'fit',
    maximizable: true,
    modal: true,

    config: {
        /**
         * @cfg
         * The {@link devilry.extjshelpers.RestfulSimplifiedEditPanel} to use for editing.
         */
        editpanel: undefined
    },
    
    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },
    
    initComponent: function() {
        var me = this;

        var form = this.editpanel.down('form');
        if(!this.width && form.suggested_windowsize) {
            this.width = form.suggested_windowsize.width,
            this.height = form.suggested_windowsize.height
        }

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
