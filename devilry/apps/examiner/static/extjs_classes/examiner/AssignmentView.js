Ext.define('devilry.examiner.AssignmentView', {
    extend: 'Ext.panel.Panel',

    config: {
        assignment_recordcontainer: undefined,
        assignmentmodelname: undefined,
        assignmentid: undefined,
        assignmentgroupstore: undefined
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
               menu: [],
               listeners: {
                   scope: this,
                   click: this.onStudents
               }
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

    onStudents: function(button) {
        var studentswindow = Ext.create('Ext.window.Window', {
            title: 'Students',
            width: 926,
            height: 500,
            layout: 'fit',
            maximizable: true,
            modal: true,
            items: {
                xtype: 'studentsmanager',
                assignmentgroupstore: this.assignmentgroupstore,
                assignmentid: this.assignmentid,
                isAdministrator: false
            },
            listeners: {
                scope: this,
                close: function() {
                    button.toggle(false);
                }
            }
        });
        studentswindow.show();
        studentswindow.alignTo(button, 'bl', [0, 0]);
    }
});
