{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form', // Does not have to be a form. More complex config editors will probably use a panel with more complex layouts than what forms support.
    help: '<h2>Introduction:</h2><p>'+
        'In this gradeeditor you can create your own form for correcting assignments. You can do this by adding various fields in the textbox.'+
        '\nFields are structured like this:</p><p>'+
        '<pre>fieldtype : points\n'+
        'fieldlabel\n'+
        ';;\n</pre></p><p>'+
        '\nThere are two different types of fields:'+
        '</p><h3>Numberfield:</h3><p>'+
        'A numberfield is a field where an examiner sets the number of points earned in this part of the assignment. A numberfield is defined like this:'+
        '</p><p>'+
        '<pre>number : 42\n'+
        'Enter number of points for part 1.1:\n'+
        ';;\n</pre></p><p>'+
        '\nIn this case <em>number</em> specifies that you want a numberfield, <em>42</em> is the maximum number of points one can achieve in this part of the assignment, and '+
        '<em>Enter number of points for part 1.1:</em> is the information shown to the examiner for this field.</p>'+
        '<h3>Checkbox:</h3><p>'+
        'A checkbox is ideal for <em>Approved/Not approved</em> scenarios, since its either checked or not! A checkbox is defined much like the numberfield:'+
        '</p><p>'+
        '<pre>check : 42\n'+
        'Is part 1.1 approved?\n'+
        ';;</pre></p><p>'+
        '\nBut here you type <em>check</em> to specify that you want a numberfield, and <em>42</em> is the number of points one will get if the examiner checks the checkbox! And '+
        '<em>Is part 1.1 approved?</em> is the information shown to the examiner for this field.'+
        '</p>'+
        '<h3>Points to pass</h3>'+
        '<p>In this field you simply enter how many points in total a student needs to pass the assignment. The points earned in the fields you define above will be summed up and tested '+
        'against this number.</p>',
        
    
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
            fieldLabel: 'Points to pass',
            flex: 0,
            minValue: 0
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
            var grade = gradestring[i] + "";
            var gradearray = grade.split(',');
            retval = retval+gradearray[0]+" : "+gradearray[1] +'\n'+gradearray[2]+'\n;;\n';
        }

        return retval;
    },
    
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
