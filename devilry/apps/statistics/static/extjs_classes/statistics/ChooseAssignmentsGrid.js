Ext.define('devilry.statistics.ChooseAssignmentsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-chooseassignmentsgrid',
    hideHeaders: true,
    title: 'Choose assignments',

    requires: [
        'devilry.extjshelpers.GridSelectionModel'
    ],

    config: {
        selectedAssignmentIds: undefined
    },
    
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
            }],
            listeners: {
                scope: this,
                render: function() {
                    if(this.selectedAssignmentIds) {
                        this._selectByIds(this.selectedAssignmentIds);
                    }
                }
            }
        });
        this.callParent(arguments);
    },

    _selectByIds: function(assignmentIds) {
        var records = [];
        Ext.each(assignmentIds, function(assignmentId, index) {
            var record = this.store.getById(assignmentId);
            records.push(record);
        }, this);
        try {
            this.getSelectionModel().select(records);
        } catch(e) {
            Ext.defer(function() {
                this._selectByIds(assignmentIds);
            }, 300, this);
        }
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
