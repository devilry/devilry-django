Ext.define('devilry.gradeeditors.DraftEditorWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.gradedrafteditor',
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


    initComponent: function() {
        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    text: 'Save draft',
                    scale: 'large',
                    iconCls: 'icon-save-32',
                    listeners: {
                        scope: this,
                        click: this.onSaveDraft,
                    }
                }, {
                    xtype: 'button',
                    text: 'Publish',
                    scale: 'large',
                    iconCls: 'icon-add-32',
                    listeners: {
                        scope: this,
                        click: this.onPublish
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    /**
     * @private
     * Get the draft editor.
     */
    getDraftEditor: function() {
        return this.getComponent(0).getComponent(0);
    },

    /**
     * @private
     * Call the onPublish() method in the draft editor.
     */
    onPublish: function() {
        this.getDraftEditor().onPublish();
    },

    /**
     * @private
     * Call the onSaveDraft() method in the draft editor.
     */
    onSaveDraft: function() {
        this.getDraftEditor().onSaveDraft();
    },

    /**
     * @private
     * Exit the grade editor.
     */
    exit: function() {
        this.close();
    },

    /**
     * @private
     */
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

    /**
     * Save the current draft.
     */
    saveDraft: function(draft, onFailure) {
        this.save(false, draft, {
            scope: this.getDraftEditor(),
            failure: onFailure
        });
    },

    /**
     * Save and publish draft.
     *
     * @param onFailure
     */
    saveDraftAndPublish: function(draft, onFailure) {
        var me = this;
        this.save(true, draft, {
            scope: this.getDraftEditor(),
            success: function(response) {
                me.exit();
            },
            failure: onFailure
        });
    }
});
