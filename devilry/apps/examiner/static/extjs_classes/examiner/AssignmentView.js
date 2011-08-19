Ext.define('devilry.examiner.AssignmentView', {
    extend: 'Ext.panel.Panel',

    config: {
        assignment_recordcontainer: undefined,
        assignmentmodelname: undefined,
        assignmentid: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        Ext.apply(this, {
            tbar: [{
               xtype: 'button',
               scale: 'large',
               text: 'Students',
               menu: []
            }],
            items: []
        });
        this.callParent(arguments);

        var assignmentmodel = Ext.ModelManager.getModel(this.assignmentmodelname);
        assignmentmodel.load(this.assignmentid, {
            scope: this,
            success: this.onLoadAssignmentSuccess,
            failure: this.onLoadAssignmentFailure
        });
    },


    onLoadAssignmentSuccess: function(record) {
        this.assignment_recordcontainer.setRecord(record);
    },

    onLoadAssignmentFailure: function() {
        throw "Failed to load assignment";
    },
});
