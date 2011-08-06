{
    padding: 20,
    border: false,
    frame: false,
    xtype: 'form', // Does not have to be a form. More complex config editors will probably use a panel with more complex layouts than what forms support.

    initializeEditor: function(config) {
        this.getMainWin().changeSize(400, 200); // Change window size to a more appropritate size for so little content.

        // Load configuration, and fall back on defaults
        var configobj = {
            defaultvalue: false,
            fieldlabel: 'Approved'
        };
        if(config.config) {
            configobj = Ext.JSON.decode(config.config);
        }

        // Create and add the fields
        this.defaultvalueField = Ext.widget('checkboxfield', {
            boxLabel: 'Choose default value',
            checked: configobj.defaultvalue
        });
        this.add(this.defaultvalueField);

        this.fieldlabelField = Ext.widget('textfield', {
            fieldLabel: 'Field label',
            labelWidth: 80,
            width: 340,
            value: configobj.fieldlabel
        });
        this.add(this.fieldlabelField);

        this.getEl().unmask(); // Unmask the loading mask (set by the main window).
    },

    /**
     * Called when the 'Save' button is clicked.
     */
    onSave: function() {
        if (this.getForm().isValid()) {
            var config = Ext.JSON.encode({
                defaultvalue: this.defaultvalueField.getValue(),
                fieldlabel: this.fieldlabelField.getValue()
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
}
