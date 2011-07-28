Ext.define('devilry.extjshelpers.DraftEditorWindow', {
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
        deliveryid: undefined,

        /**
         * @cfg
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false
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
        var classname = Ext.String.format(
            'devilry.apps.gradeeditors.simplified.{0}.SimplifiedFeedbackDraft',
            this.isAdministrator? 'administrator': 'examiner'
        );
        var staticfeedback = Ext.create(classname, {
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
