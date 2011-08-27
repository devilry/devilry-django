{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form',

    help: '<h3>Is the assignment approved:</h3>' +
        '<p>Mark the checkbox if the assignment is approved</p>' + 
        '<h3>Enter feedback:</h3>'+
        '<p>Here you enter a feedback to the student. What was good, what was bad etc..</p>',
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
        this.textarea = Ext.widget('textareafield', {
            fieldLabel: 'Enter feedback',
            flex: 1
        });
        this.add(this.checkbox);
        this.add(this.textarea);
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
            var buf = Ext.JSON.decode(draftstring);
            var approved = buf[0];
            var feedback = buf[1];
            this.checkbox.setValue(approved);
            this.textarea.setValue(feedback);
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
        retval[0] = approved
        retval[1] = feedback
        var draft = Ext.JSON.encode(retval);
        return draft;
    }
}
