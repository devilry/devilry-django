{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form',

    layout: {
        type: 'vbox',
        align: 'stretch',
        autoSize: true,
    },
   // layout: 'auto',
    autoScroll: true,

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold;'
    },
    defaults: {
        margins: '0 0 5 0'
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
        this.formVal = this.editorConfig.formValues;
        this.draftfields = [];
        var nr = 0;
        var i=0;
        
        for (i=0; i<this.formVal.length; i++) {
            var grade = this.formVal[i];
            if (grade[0] == 'check') {
                var field = Ext.widget('checkboxfield', {
                    boxLabel: grade[3] + " (" + grade[1] + ")",
                    checked: parseInt(grade[2]),
                    anchor: '-1',
                    flex: 0
                });
                this.draftfields[nr] = field;
                this.add(field)
                nr++;
            } else if (grade[0] == 'number'){
                var field = Ext.widget('numberfield', {
                    fieldLabel: grade[3],
                    anchor: '-1',
                    value: grade[2],
                    flex: 0
                });
                this.draftfields[nr] = field;
                this.add(field)
                nr++;
            } else if (grade[0] == 'label'){
                var field = Ext.widget('label', {
                    text: grade[3],
                    anchor: '-1',
                    flex: 0,
                    style: {
                        fontWeight: 'bold',
                        fontSize: '1.2em',
                        margin: '10 0 10 0',
                    },
                });
                this.add(field)
            } else if (grade[0] == 'text') {
                var label = Ext.widget('label', {
                    text: grade[3] + ":",
                    anchor: '-1',
                    flex: 0,
                    style: {
                        fontWeight: 'bold',
                    },
                });
                var field = Ext.widget('markdownfulleditor', {
                    height: 150
                });
                this.draftfields[nr] = field;
                this.add(label)
                this.add(field)
                nr++;
            }
        }

        //this.feedback = Ext.widget('markdownfulleditor', {
        //    height: 200
        //});
        //this.add(this.feedback);
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
        if(buf.gradeeditor && buf.gradeeditor.id === 'commentform') {
            var i=0;
            var nr = 0;
            for (i=0; i<buf.values.length; i++) {
                var grade = this.formVal[i];
                if(grade[0] != 'label') {
                    this.draftfields[nr].setValue(buf.values[nr]);
                    nr++;
                }
            }
            //this.feedback.setValue(buf.feedback);
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
        if(draftstring != undefined) {
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
        //var feedback = this.feedback.getValue();
        var values = [];
        var i=0;
        for (i=0; i<this.draftfields.length; i++) {
            values[i] = this.draftfields[i].getValue();
        }
        
        var retval = {
            gradeeditor: {
                id: 'commentform',
                version: '1.0'
            },
            values: values,
            feedback: ""
        };

        var draft = Ext.JSON.encode(retval);
        return draft;
    }
}
