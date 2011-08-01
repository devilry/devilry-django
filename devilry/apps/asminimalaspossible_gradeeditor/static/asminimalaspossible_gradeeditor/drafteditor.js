{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form',
    items: [{
        xtype: 'checkboxfield',
        boxLabel: 'Approved',
        id: 'approved-checkbox'
    }],

    listeners: {
        /**
         * Resize window to make it more appropriate for the minimal amount of
         * content.
         */
        render: function() {
            this.getGradeDraftEditor().changeSize(300, 200);
        }
    },

    /**
     * @private
     * Get the grade draft editor main container.
     */
    getGradeDraftEditor: function() {
        return this.up('gradedrafteditor');
    },

    /**
     * @private
     * Used by onSaveDraft and onPublish to handle save-failures.
     */
    onFailure: function() {
        console.error('Failed!');
    }


    /**
     * @private
     * Create a draft (used in onSaveDraft and onPublish)
     */
    createDraft: function() {
        var approved = Ext.getCmp('approved-checkbox').getValue();
        var draft = Ext.JSON.encode(approved);
        return draft;
    },

    /**
     * Called when the 'save draft' button is clicked.
     */
    onSaveDraft: function() {
        if (this.getForm().isValid()) {
            var draft = this.createDraft();
            this.getGradeDraftEditor().saveDraft(draft, this.onFailure);
        }
    },

    /**
     * Called when the publish button is clicked.
     */
    onPublish: function() {
        if (this.getForm().isValid()) {
            var draft = this.createDraft();
            this.getGradeDraftEditor().saveDraftAndPublish(draft, this.onFailure);
        }
    }
}
