
{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form', // Does not have to be a form. More complex config editors will probably use a panel with more complex layouts than what forms support.
    help: '<h3>Points to pass assignment:</h3>'+
        '<p>This is where you enter the minimum number of points needed to pass this assignment.</p>'+
        '<h3>Maximum number of points:</h3>'+
        '<p>This is where you enter the maximum number of points one can get for this assignment.</p>'+
        '<h3>Grades:</h3>'+
        '<p>In this gradeeditor you define your own grades, and the points needed to achieve every grade.\n'+
        'A grade is defined by a line like this:</p>'+
        '<pre>Approved:40</pre><p>Where the grade is <em>Approved</em>, and you will need 30 or more points to get this grade.</p>'+
        '<p>So if you want to make an assignment where the grading is <em>Approved/Not approved</em> you '+
        'can enter this:</p>'+
        '<pre>Approved: 30\nNot approved: 0</pre>'+
        '<p>and deliveries given 30 points or more will get the grade <em>Approved</em> '+
        'and deliveries with 0-29 points will get the grade <em>Not approved</em>.</p>'+
        '<p>You can enter as many grades as you want, so if you want grades A-F you can do that the same way:</p>'+
        '<pre>'+
        'A : 50\nB : 40\nC : 30\nD : 20\nE : 10\nF : 0'+
        '</pre>',
    
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
            grades: 'Press help for example'
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
            this.gradeField.setValue(this.parseGradeValue(configobj.grades));
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

    parseGradeValue: function(gradestring) {
        var retval = '';
        var i=0;
        for (i=0; i<gradestring.length; i++) {
            if (i != 0) {
                retval = retval + '\n';
            }
            var grade = gradestring[i] + "";
            var gradearray = grade.split(',');
            retval = retval+gradearray[0]+" : "+gradearray[1];
        }

        return retval;
    },
    
    parseTextToGradeList: function(rawValue) {
        var asArray = rawValue.split('\n');
        var resultArray = [];
        var me = this;
        Ext.Array.each(asArray, function(line) {
            line = Ext.String.trim(line);
            var split = line.split(/\s*:\s*/, 2);
            if(split != '') {
                resultArray.push(split);
            }
        });
        return resultArray;
    },
}
