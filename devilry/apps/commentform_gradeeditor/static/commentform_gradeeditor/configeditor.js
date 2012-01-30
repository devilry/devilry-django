{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form', // Does not have to be a form. More complex config editors will probably use a panel with more complex layouts than what forms support.
    help: '<h1>Introduction:</h1><p>'+
        'In this grade editor you define a list of positive and negative feedback to the students. The examiners may make any selection from the list and their selections will be presented to the students. Each feedback element may give or take a defined number of points which are added up and compared against a minimum to get the assignment approved.</p>\n'+
        '<h2>Points required to pass</h2>'+
        '<p>Fill in the number of points in total a student needs to pass the assignment. The points earned in the fields you define (see below) will be summed up and tested '+
        'against this number.</p>' +
        '<h2>Set up the feedback list</h2>\n' +
        '<p>Each element in the feedback list is defined as a checkbox. This resembels the syntax in the Simple Schema/Form grade editor. A feedback element is structured like this:</p>\n' +
        '<p><pre>check : points : default\n' +
        'comment\n' +
        ';;\n</pre></p>' +
        '<p>The number of points may be any integer number, both positive and negative. The default may be either 0 or 1, to enable or disable the feedback element by default. The comment is visible for both the examiner and student.</p>\n' +
        '<h2>Set up an adjustment field</h2>\n' +
        '<p>In case you want to give the examiners an option to adjust the final number of given points, you may define a number field to adjust the sum calculated by the above feedback fields. This can for instance be used if the examiners finds errors or positive remarks that are not defined in the feedback list. This field will be shown to the student with the text you give in the definition.</p>\n' +
        '<p><pre>number : maxpoints : default\n' +
        'comment\n' +
        ';;\n</pre></p>' + 
        '<p>The comment is shown to the student. The max points field is currently not in use, so the examiner may actually set any number of points. This might change in the future.</p>\n' +
        '<h2>A working example</h2>\n' +
        'Below is a working example that may be used as a reference for making your own feedback list.\n' +
        '<p><pre>' +
        'check : 10 : 1\n' +
        'You have remembered to include a figure. That is good.\n' +
        ';;\n' +
        'check : 20 : 0\n' +
        'Your conclusion is well written. I believe you have understood the problem correctly.\n' +
        ';;\n' +
        'check : -10 : 0\n' +
        'The program you have written does not compile.\n' +
        ';;\n' +
        'check : -20 : 0\n' +
        'You have not answered the discussion questions.\n' +
        ';;\n' +
        'number : 0 : 0\n' +
        'Correction points (see comment).\n'+
        ';;' +
        '</pre></p>', 
    
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
            fieldLabel: 'Specify fields',
            flex: 1,
            emptyText: 'See help for examples'
        });
        this.add(this.formArea);
        
        this.approvedLimitField = Ext.widget('numberfield', {
            fieldLabel: 'Points required to pass',
            flex: 0
        });
        this.add(this.approvedLimitField);
        if(config.config) {
            configobj = Ext.JSON.decode(config.config);
            this.formArea.setValue(this.parseFormToText(configobj.formValues));
            this.approvedLimitField.setValue(configobj.approvedLimit);
        }
        
        this.getEl().unmask(); // Unmask the loading mask (set by the main window).
    },
        
    /**
     * Called when the 'Save' button is clicked.
     */
    onSave: function() {
        if (this.getForm().isValid()) {
            var config = Ext.JSON.encode({
                formValues: this.parseTextToForm(this.formArea.getValue()),
                approvedLimit: this.approvedLimitField.getValue()
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

    parseFormToText: function(gradestring) {
        var retval = '';
        var i=0;
        for (i=0; i<gradestring.length; i++) {
            var gradearray = gradestring[i];
            // var gradearray = grade.split(',');
            retval = retval+gradearray[0]+" : "+gradearray[1] + " : " + gradearray[2] +'\n' + gradearray[3]+'\n;;\n\n';
        }

        return retval;
    },
    
    parseTextToForm: function(rawValue) {
        rawValue = rawValue+'\n';
        var asArray = rawValue.split(';;\n');
        var resultArray = [];
        var i=0;
        for (i=0; i<asArray.length; i++) {
            var split = Ext.String.trim(asArray[i]);
            split = split.split('\n');
            var grade = split[0];
            grade = Ext.String.trim(grade);
            grade = grade.split(/\s*:\s*/, 3);
            
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
