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

    /* Resize window to make it more appropriate for the minimal amount of content. */
    listeners: {
        render: function() {
            var gradedrafteditor = this.up('gradedrafteditor');
            gradedrafteditor.changeSize(300, 200);
        }
    },


    /* Create a draft (used in onSaveDraft and onPublish) */
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
            var gradedrafteditor = this.up('gradedrafteditor');
            gradedrafteditor.saveDraft(draft, this.onFailure);
        }
    },

    /**
     * Called when the publish button is clicked.
     */
    onPublish: function() {
        if (this.getForm().isValid()) {
            var draft = this.createDraft();
            var gradedrafteditor = this.up('gradedrafteditor');
            gradedrafteditor.saveDraftAndPublish(draft, this.onFailure);
        }
    },

    onFailure: function() {
        console.error('Failed!');
    }
}
