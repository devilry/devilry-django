{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form',
    
    help: '<h3>Is the assignment approved:</h3>' +
        '<p>Mark the checkbox if the assignment is approved</p>' + 
        '<h3>Enter points:</h3>'+
        '<p>Here you have to select or enter the number of points earned in the assignment.</p>'+
        '<p>Any grade in Devilry is represented as a number, however this number is mainly for statistical purposes, '+
        'and will not be visible to the students.</p>'+
        '<h3>Enter grade:</h3>'+
        '<p>This is where you enter the grade earned in the assignment.</p>'+
        '<p>A grade is a very short text that students can view. Usually something like:</p>'+
        '<p><em>A</em>, <em>Approved</em> or <em>7/10</em>.</p>'+
        '<h3>Enter feedback:</h3>'+
        '<p>Here you enter a feedback to the student. What was good, what was bad etc..</p>',

    //items: [{
        //xtype: 'checkboxfield',
        //boxLabel: 'Approved',
        //id: 'approved-checkbox'
    //}],

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
        this.grade = Ext.widget('textfield', {
            fieldLabel: 'Enter grade',
            flex: 0
        });
        this.points = Ext.widget('numberfield', {
            fieldLabel: 'Enter points',
            minValue: 0,
            flex: 0
        });
        this.textarea = Ext.widget('markdownfulleditor', {
            fieldLabel: 'Enter feedback',
            flex: 1
        });
        this.add(this.checkbox);
        this.add(this.points);
        this.add(this.grade);
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
            var points = buf[1];
            var grade = buf[2];
            var feedback = buf[3];
            this.checkbox.setValue(approved);
            this.points.setValue(points);
            this.grade.setValue(grade);
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
        var points = this.points.getValue();
        var grade = this.grade.getValue();
        var feedback = this.textarea.getValue();
        var retval = new Array();
        retval[0] = approved;
        retval[1] = points;
        retval[2] = grade;
        retval[3] = feedback;
        var draft = Ext.JSON.encode(retval);
        return draft;
    }
}
