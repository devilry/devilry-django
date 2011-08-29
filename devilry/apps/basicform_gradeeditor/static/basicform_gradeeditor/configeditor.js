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
        this.formArea = Ext.widget('textareafield', {
            fieldLabel: 'Enter formfields',
            flex: 1,
            emtyText: 'See help for examples'
        });
        this.add(this.formArea);
        
        //if(config.config) {
            //configobj = Ext.JSON.decode(config.config);
            //this.formArea.setValue(this.parseFormToText(configobj.form));
        //}
        
        this.getEl().unmask(); // Unmask the loading mask (set by the main window).
    },
        
    /**
     * Called when the 'Save' button is clicked.
     */
    onSave: function() {
        if (this.getForm().isValid()) {
            var config = Ext.JSON.encode({
                formValues: this.parseTextToForm(this.formArea.getValue()),
            });
            this.getMainWin().saveConfig(config);
        }
    },

    /**
     * @private
     * Get the grade config editor main window.
     */
    getMainWin: function() {
        return this.up('gradeconfigeditormainwin');
    },

    //parseFormToText: function(gradestring) {
        //var retval = '';
        //var i=0;
        //for (i=0; i<gradestring.length; i++) {
            //if (i != 0) {
                //retval = retval + '\n';
            //}
            //var grade = gradestring[i] + "";
            //var gradearray = grade.split(',');
            //retval = retval+gradearray[0]+" : "+gradearray[1];
        //}

        //return retval;
    //},
    
    parseTextToForm: function(rawValue) {
        rawValue = rawValue+'\n';
        var asArray = rawValue.split(';;\n');
        var resultArray = [];
        var i=0;
        for (i=0; i<asArray.length; i++) {
            var split = asArray[i].split('\n');
            var grade = split[0];
            grade = Ext.String.trim(grade);
            grade = grade.split(/\s*:\s*/, 2);

            if (grade != '') {
                var label = "";
                var j=0;
                for (j=1; j<split.length; j++) {
                    labelpart = split[j];
                    labelpart = Ext.String.trim(labelpart);
                    
                    if (labelpart != '') {
                        if (label != ''){
                            label = label + ' ';
                        }
                        label = label + labelpart;
                    }
                }

                grade.push(label);
                resultArray.push(grade);
            }
        }
        
        return resultArray;
    },
}
