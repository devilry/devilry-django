{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'panel', // Does not have to be a form. More complex config editors will probably use a panel with more complex layouts than what forms support.
    
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

    typetemplate: Ext.create('Ext.XTemplate',
        '<tpl if="type == \'Markdown\'">',
        '   <pre>{settings.text}</pre>',
        '</tpl>',
        '<tpl if="type == \'Boolean\'">',
        '   <p>Points given if passed: {settings.trueValue}</p>',
        '   <p>Labels: {settings.labels}</p>',
        '</tpl>',
        '<tpl if="type == \'Select\'">',
        '   <p>Values: ',
        '       <tpl for="settings.values">',
        '           <p>{label}: {value} </p>',
        '       </tpl>',
        '   </p>',
        '</tpl>'
    ),
    /**
     * Called by the config-editor main window when it is opened.
     *
     * @param config Get the grade editor configuration that is stored on the
     *      current assignment.
     */
    initializeEditor: function(config) {
        var me = this;
        this.store = Ext.create('Ext.data.Store', {
            fields:['type', 'settings'],
            data:{'items':[
                {"type":"Markdown",
                    "settings": {
                        text: "Some markdown-text-stuff"
                    }
                },
                {"type":"Boolean", 
                    "settings":{
                        trueValue: 30,
                        labels: ["No", "Yes"]
                    }
                },
                {"type":"Select", 
                    "settings":{
                        values: [
                            {value: 0, label: "No"},
                            {value: 20, label: "Somewhat"},
                            {value: 30, label: "Yes"}
                        ]
                    }
                }
                ]},
                proxy: {
                    type: 'memory',
                    reader: {
                        type: 'json',
                        root: 'items'
                    }
                }
        });

        this.grid = Ext.create('Ext.grid.Panel', {
            title: 'Gradeform',
            store: this.store,
            columns: [
                {header: 'Type',  dataIndex: 'type'},
                {header: 'Settings', dataIndex: 'type', flex: 1,
                    renderer: function(value, metaData, settings) {
                        return me.typetemplate.apply(settings.data);
                    }
                }
            ],
            height: 200,
            width: 400,
            renderTo: Ext.getBody()
        });
        this.add(this.grid);

        this.markdownbutton = Ext.create('Ext.Button', {
            text     : 'Add markdown-field',
            renderTo : Ext.getBody(),
            listeners: {
                click: function() {
                    this.setText('I was clicked!');
                }
            }
        });
        this.add(this.markdownbutton);
        
        this.booleanbutton = Ext.create('Ext.Button', {
            text     : 'Add boolean-field',
            renderTo : Ext.getBody(),
            listeners: {
                click: function() {
                    this.setText('I was clicked!');
                }
            }
        });
        this.add(this.booleanbutton);
        
        this.selectbutton = Ext.create('Ext.Button', {
            text     : 'Add select-field',
            renderTo : Ext.getBody(),
            listeners: {
                click: function() {
                    this.setText('I was clicked!');
                }
            }
        });
        this.add(this.selectbutton);
        
        this.getEl().unmask(); // Unmask the loading mask (set by the main window).
    },

    /**
     * Called when the 'Save' button is clicked.
     */
    onSave: function() {
        //if (this.getForm().isValid()) {
            //var config = Ext.JSON.encode({
                //maxpoints: this.maxpointsField.getValue(),
                //approvedlimit: this.approvedlimitField.getValue(),
                //grades: this.parseTextToGradeList(this.gradeField.getValue()),
            //});
            //this.getMainWin().saveConfig(config, this.onFailure);
        //}
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

    //parseGradeValue: function(gradestring) {
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
    
    //parseTextToGradeList: function(rawValue) {
        //var asArray = rawValue.split('\n');
        //var resultArray = [];
        //var me = this;
        //Ext.Array.each(asArray, function(line) {
            //line = Ext.String.trim(line);
            //var split = line.split(/\s*:\s*/, 2);
            //if(split != '') {
                //resultArray.push(split);
            //}
        //});
        //return resultArray;
    //},
}
