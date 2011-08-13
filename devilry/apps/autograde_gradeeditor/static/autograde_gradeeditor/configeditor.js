
{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form', // Does not have to be a form. More complex config editors will probably use a panel with more complex layouts than what forms support.
    
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
     * Called by the config-editor main window when it is opened.
     *
     * @param config Get the grade editor configuration that is stored on the
     *      current assignment.
     */
    //'maxpoints'
    //'approvedlimit'
    //'grades'
    //'pointlabel'
    //'feedbacklabel'

    initializeEditor: function(config) {
        this.getMainWin().changeSize(500, 500); 

        // Load configuration, and fall back on defaults
        var configobj = {
            maxpoints: 100,
            approvedlimit: 60,
            pointlabel: 'Enter points',
            feedbacklabel: 'Enter feedback',
            grades: 'approved: 60\nnot approved: 0'
        };
        if(config.config) {
            configobj = Ext.JSON.decode(config.config);
        }

        // Create and add the fields
        this.pointlabelField = Ext.widget('textfield', {
            fieldLabel: 'Points label',
            flex: 0,
            value: configobj.pointlabel
        });
        this.add(this.pointlabelField);
        
        this.feedbacklabelField = Ext.widget('textfield', {
            fieldLabel: 'Feedback label',
            flex: 0,
            value: configobj.feedbacklabel
        });
        this.add(this.feedbacklabelField);

        this.approvedlimitField = Ext.widget('numberfield', {
            fieldLabel: 'Points to pass assignment',
            flex: 0,
            value: configobj.approvedlimit
        });
        this.add(this.approvedlimitField);
        
        this.maxpointsField = Ext.widget('numberfield', {
            fieldLabel: 'Maximum number of points',
            flex: 0,
            value: configobj.maxpoints
        });
        this.add(this.maxpointsField);

        this.gradeField = Ext.widget('textareafield', {
            fieldLabel: 'Grades',
            flex: 1,
            value: configobj.grades
        });
        this.add(this.gradeField);

        this.getEl().unmask(); // Unmask the loading mask (set by the main window).
    },

    /**
     * Called when the 'Save' button is clicked.
     */
    onSave: function() {
        if (this.getForm().isValid()) {
            var config = Ext.JSON.encode({
                maxpoints: this.maxpointsField.getValue(),
                approvedlimit: this.approvedlimitField.getValue(),
                grades: this.parseTextToGradeList(this.gradeField.getValue()),
                pointlabel: this.pointlabelField.getValue(),
                feedbacklabel: this.feedbacklabelField.getValue()
            });
            this.getMainWin().saveConfig(config, this.onFailure);
        }
    },

    /**
     * @private
     * Get the grade config editor main window.
     */
    getMainWin: function() {
        return this.up('gradeconfigeditormainwin');
    },

    /**
     * @private
     * Used by onSave to handle save-failures.
     */
    onFailure: function() {
        console.error('Failed!');
    },
    
    parseTextToGradeList: function(rawValue) {
        var asArray = rawValue.split('\n');
        var resultArray = [];
        var me = this;
        Ext.Array.each(asArray, function(line) {
            line = Ext.String.trim(line);
            var split = line.split(/\s*:\s*/, 2);
            resultArray.push(split);
        });
        return resultArray;
    },
}
