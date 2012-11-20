Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Manual', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',

    msgTpl: Ext.create('Ext.XTemplate',
        '<div class="readable-section">',
        'Choose the students that qualifies for final exams, and click <strong>Save</strong>. ',
        'Press the <em>{ctrlbutton} button</em> while clicking students to select multiple students.',
        '<div>'
    ),

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'box',
                html: this.msgTpl.apply({
                    ctrlbutton: Ext.isMac? 'CMD/Command': 'CTRL/Control'
                }),
                margin: '0 0 10 0',
                store: this.loader.assignment_store
            }, this.saveButton]
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        var selected = this._getSelectedStudents();
        return Ext.Array.contains(selected, student);
    },

    validInput: function() {
        if(this._getSelectedStudents().length === 0) {
            Ext.MessageBox.alert('Select at least one', 'Please select at least one student.');
            return false;
        }
        return true;
    },

    _getSelectedStudents: function() {
        var dataview = this.up('statistics-periodadminlayout').down('statistics-dataview');
        var selected = dataview.getSelectedStudents();
        return selected;
    }

});
