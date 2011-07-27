Ext.define('devilry.extjshelpers.GradeEditorWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.gradeeditor',
    title: 'Create feedback',
    width: 800,
    height: 600,
    layout: 'fit',
    modal: true,

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
    },

    save: function(published, draft, saveconfig) {
        var staticfeedback = Ext.create('devilry.apps.gradeeditors.simplified.administrator.SimplifiedFeedbackDraft', {
            draft: draft,
            published: published,
            delivery: this.deliveryid
        });
        staticfeedback.save(saveconfig, saveconfig);
    },

    saveDraft: function(draft, onFailure) {
        this.save(false, draft, {
            failure: onFailure
        });
    },

    saveDraftAndPublish: function(draft, onFailure) {
        var me = this;
        this.save(true, draft, {
            success: function(response) {
                console.log("Success");
                console.log(response.data);
                me.exit();
            },
            failure: onFailure
        });
    }
});
