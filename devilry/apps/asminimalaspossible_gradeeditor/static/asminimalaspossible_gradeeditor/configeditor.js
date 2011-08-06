{
    xtype: 'form',
    border: false,
    items: [{
        xtype: 'checkboxfield',
        boxLabel: 'Default value',
        id: 'defaultvalue'
    }, {
        xtype: 'textarea',
        fieldLabel: 'Field label',
        id: 'fieldlabel'
    }],


    initializeEditor: function(config) {
        this.getMainWin().changeSize(300, 200); // Change window size to a more appropritate size for so little content.

        //this.editorConfig = Ext.JSON.decode(config.config);
        //this.add(this.checkbox);
        this.getEl().unmask(); // Unmask the loading mask (set by the main window).
    },

    /**
     * @private
     * Get the grade config editor main window.
     */
    getMainWin: function() {
        return this.up('gradeconfigeditormainwin');
    },
}
