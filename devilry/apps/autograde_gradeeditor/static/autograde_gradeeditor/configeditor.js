
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
    initializeEditor: function(config) {
        //this.getMainWin().changeSize(500, 500); 

        // Load configuration, and fall back on defaults
        var configobj = {
            maxpoints: 'Example: 100',
            approvedlimit: 'Example: 60',
            grades: 'Example: approved: 60'
        };

        // Create and add the fields
        this.approvedlimitField = Ext.widget('numberfield', {
            fieldLabel: 'Points to pass assignment',
            flex: 0,
            emptyText: configobj.approvedlimit
        });
        this.add(this.approvedlimitField);
        
        this.maxpointsField = Ext.widget('numberfield', {
            fieldLabel: 'Maximum number of points',
            flex: 0,
            emptyText: configobj.maxpoints
        });
        this.add(this.maxpointsField);

        this.gradeField = Ext.widget('textareafield', {
            fieldLabel: 'Grades',
            flex: 1,
            emptyText: configobj.grades
        });
        this.add(this.gradeField);

        if(config.config) {
            configobj = Ext.JSON.decode(config.config);
            this.approvedlimitField.setValue(configobj.approvedlimit);
            this.maxpointsField.setValue(configobj.maxpoints);
            this.gradeField.setValue(this.getGradeValue(configobj.grades));
        }

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

    getGradeValue: function(rawvalue) {
        var asArray = rawValue.split(',');
        var retval = '';
        for (int i=0; i<asArray.length; i++) {
            retval = retval + asArray[i] + ':'+asArray[i+1] + '\n';
            i++;

        return retval;
        }
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
