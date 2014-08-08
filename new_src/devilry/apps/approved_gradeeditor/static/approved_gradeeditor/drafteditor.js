{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form',

    help: '<h3>Is the assignment approved:</h3>' +
        '<p>Mark the checkbox if the assignment is approved</p>' + 
        '<h3>Enter feedback:</h3>'+
        '<p>Here you enter a feedback to the student. What was good, what was bad etc. For help on how to format the feedback text, click the question button in the upper right corner of the feedback editor.</p>',
    //helpwidth: 500,
    //helpheight: 300,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },
    defaults: {
        margins: '0 0 10 0'
    },
    /**
     * Called by the grade-editor main window just before calling
     * setDraftstring() for the first time.
     *
     * @param config Get the grade editor configuration that is stored on the
     *      current assignment.
     */
    initializeEditor: function() {
        this.checkbox = Ext.widget('checkboxfield', {
            boxLabel: 'Is the assignment approved?',
            flex: 0
        });
        //this.textarea = Ext.widget('textareafield', {
            //fieldLabel: 'Enter feedback',
            //flex: 1
        //});
        this.textarea = Ext.widget('markdownfulleditor', {
            flex: 1,
            title: 'Enter feedback'
        });

        this.add(this.checkbox);
        this.add(this.textarea);
    },

    /**
     * @private
     */
    parseDraftString: function(draftstring) {
        try {
            var buf = Ext.JSON.decode(draftstring);
        } catch(e) {
            // The current draft string is not JSON, proceed as if no draft string
            return;
        }
        if(buf.gradeeditor && buf.gradeeditor.id === 'approved') {
            this.checkbox.setValue(buf.approved);
            this.textarea.setValue(buf.feedback);
        }
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
            this.checkbox.setValue(true);
        } else {
            this.parseDraftString(draftstring);
        }
        this.getEl().unmask(); // Unmask the loading mask (set by the main window).
    },

    /**
     * Called when the 'save draft' button is clicked.
     */
    onSaveDraft: function() {
        if (this.getForm().isValid()) {
            var draft = this.createDraft();
            this.getMainWin().saveDraft(draft);
        }
    },

    /**
     * Called when the publish button is clicked.
     */
    onPublish: function() {
        if (this.getForm().isValid()) {
            var draft = this.createDraft();
            this.getMainWin().saveDraftAndPublish(draft);
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
     * Create a draft (used in onSaveDraft and onPublish)
     */
    createDraft: function() {
        var approved = this.checkbox.getValue();
        var feedback = this.textarea.getValue();
        var retval = new Array();
        var draft = Ext.JSON.encode({
            gradeeditor: {
                id: 'approved',
                version: '1.0'
            },
            approved: approved,
            feedback: feedback
        });
        return draft;
    }
}
