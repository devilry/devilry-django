{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form',
    help: '<h3>Enter points:</h3>'+
        '<p>Here you have to select or enter the number of points earned in the assignment.</p>'+
        '<p>Any grade in Devilry is represented as a number, however this number is mainly for statistical purposes, '+
        'and will not be visible to the students. In this assignments studens will be given their grade based on the number of points entered here.</p>'+
        '<h3>Enter feedback:</h3>'+
        '<p>Here you enter a feedback to the student. What was good, what was bad etc..</p>',

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
    initializeEditor: function(config) {
        var me = this;
        this.editorConfig = Ext.JSON.decode(config.config);
        var formVal = this.editorConfig.formValues;
        this.draftfields = [];
        var nr = 0;
        var i=0;
        for (i=0; i<formVal.length; i++) {
            var grade = formVal[i];
            if (grade[0] == 'check') {
                var field = Ext.widget('checkboxfield', {
                    boxLabel: grade[2],
                    flex: 0
                });
                this.draftfields[nr] = field;
                nr++;
            } else if (grade[0] == 'number'){
                var field = Ext.widget('numberfield', {
                    fieldLabel: grade[2],
                    minValue: 0,
                    maxValue: parseInt(grade[1]),
                    flex: 0
                });
                this.draftfields[nr] = field;
                nr++;
            }
        }

        for (i=0; i<this.draftfields.length; i++) {
            this.add(this.draftfields[i]);
        }

        this.feedback = Ext.widget('markdownfulleditor', {
            flex: 1
        });
        this.add(this.feedback);
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
        if(draftstring != undefined) {
            var buf = Ext.JSON.decode(draftstring);
            var i=0;
            for (i=0; i<buf.values.length; i++) {
                this.draftfields[i].setValue(buf.values[i]);
            }
            this.feedback.setValue(buf.feedback);
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
        var feedback = this.feedback.getValue();
        var values = [];
        var i=0;
        for (i=0; i<this.draftfields.length; i++) {
            values[i] = this.draftfields[i].getValue();
        }
        
        var retval = {values: values, feedback: feedback}

        var draft = Ext.JSON.encode(retval);
        return draft;
    }
}
