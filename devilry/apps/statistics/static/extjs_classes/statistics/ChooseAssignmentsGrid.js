Ext.define('devilry.statistics.ChooseAssignmentsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-chooseassignmentsgrid',
    hideHeaders: true,
    title: 'Choose assignments',

    requires: [
        'devilry.extjshelpers.GridSelectionModel'
    ],
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        this.selModel = Ext.create('devilry.extjshelpers.GridSelectionModel', {
            checkOnly: false
        });
        Ext.apply(this, {
            columns: [{
                header: 'Long name',  dataIndex: 'long_name', flex: 1
            }]
        });
        this.callParent(arguments);
    },

    getIdOfSelected: function() {
        var assignment_ids = [];
        Ext.each(this.getSelectionModel().getSelection(), function(assignmentRecord, index) {
            assignment_ids.push(assignmentRecord.get('id'));
        }, this);
        return assignment_ids;
    },


    checkAtLeastOneSelected: function() {
        var assignment_ids = this.getIdOfSelected();
        if(assignment_ids.length === 0) {
            Ext.MessageBox.alert('Invalid input', 'Please select at least one assignment');
            return false;
        }
        return true;
    }
});
