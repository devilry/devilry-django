{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'panel',
    layout: {
        type: 'hbox',
        align: 'stretch'
    },

    /**
     * Called by the grade-editor main window just before calling
     * setDraftstring() for the first time.
     *
     * @param config Get the grade editor configuration that is stored on the
     *      current assignment.
     */
    initializeEditor: function(config) {
        this.editorConfig = Ext.JSON.decode(config.config);
        this.checkbox = Ext.widget('checkboxfield', {
            boxLabel: this.editorConfig.fieldlabel
        });

        Ext.require('devilry.asminimalaspossible_gradeeditor.DummyWindow');
        this.add({
            xtype: 'form',
            border: false,
            flex: 7,
            items: [this.checkbox, {
                // This button opens a new window. Just to show how to load classes in a grade editor.
                xtype: 'button',
                text: 'click me',
                listeners: {
                    scope: this,
                    click: function() {
                        var win = Ext.create('devilry.asminimalaspossible_gradeeditor.DummyWindow', {
                            message: 'Just to show how to do loading of classes from draft editor!',
                            buttonLabel: 'Hello world!',
                            listeners: {
                                scope: this,
                                gotSomeValue: this.onGotSomeValue
                            }
                        });
                        win.show();
                    }
                }
            }]
        });
        this.add({
            xtype: 'box',
            flex: 3,
            html: '<section class="helpsection">This is the help for this draft editor.</section>'
        });
    },

    onGotSomeValue: function() {
        console.log(stuff);
    },

    /**
     * Called by the grade-editor main window to set the current draft. Used
     * both on initialization and when selecting a draft from history (rolling
     * back to a previous draft).
     *
     * @param draftstring The current draftstring, or ``undefined`` if no
     *      drafts have been saved yet.
     */
    setDraftstring: function(draftstring) {
        if(draftstring === undefined) {
            this.checkbox.setValue(this.editorConfig.defaultvalue);
        } else {
            var approved = Ext.JSON.decode(draftstring);
            this.checkbox.setValue(approved);
        }
        this.getEl().unmask(); // Unmask the loading mask (set by the main window).
    },

    /**
     * Called when the 'save draft' button is clicked.
     */
    onSaveDraft: function() {
        if (this.down('form').getForm().isValid()) {
            var draft = this.createDraft();
            this.getMainWin().saveDraft(draft, this.onFailure);
        }
    },

    /**
     * Called when the publish button is clicked.
     */
    onPublish: function() {
        if (this.down('form').getForm().isValid()) {
            var draft = this.createDraft();
            this.getMainWin().saveDraftAndPublish(draft, this.onFailure);
        }
    },



    /**
     * @private
     * Get the grade draft editor main window.
     */
    getMainWin: function() {
        return this.up('gradedrafteditormainwin');
    },

    /**
     * @private
     * Used by onSaveDraft and onPublish to handle save-failures.
     */
    onFailure: function(records, operation) {
        if(operation.error.status === 0) {
            Ext.MessageBox.alert('Server error', 'Could not contact the server. Please try again.');
        } else {
            Ext.MessageBox.alert('Failed to save!', 'Please try again');
        }
    },

    /**
     * @private
     * Create a draft (used in onSaveDraft and onPublish)
     */
    createDraft: function() {
        var approved = this.checkbox.getValue();
        var draft = Ext.JSON.encode(approved);
        return draft;
    }
}
