Ext.define('devilry.examiner.AssignmentView', {
    extend: 'Ext.panel.Panel',

    requires: [
        'devilry.extjshelpers.studentsmanager.StudentsManager',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList'
    ],

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
        this._todolist = Ext.widget('assignmentgrouptodolist', {
            store: this.assignmentgroupstore,
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
        });

        Ext.apply(this, {
            items: this._todolist
        });
        this.callParent(arguments);

        var assignmentmodel = Ext.ModelManager.getModel(this.assignmentmodelname);
        assignmentmodel.load(this.assignmentid, {
            scope: this,
            success: this.onLoadAssignmentSuccess,
            failure: this.onLoadAssignmentFailure
        });
        this.loadTodoList();
    },

    loadTodoList: function() {
        this._todolist.loadTodoListForAssignment(this.assignmentid);
    },

    onLoadAssignmentSuccess: function(record) {
        this.assignment_recordcontainer.setRecord(record);
        //this.onStudents();
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
                deadlinemodel: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDeadline'),
                gradeeditor_config_model: Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.examiner.SimplifiedConfig'),
                isAdministrator: false
            },
            listeners: {
                scope: this,
                close: function() {
                    if(button) {
                        button.toggle(false);
                    }
                    this.loadTodoList();
                }
            }
        });
        studentswindow.show();
        if(button) {
            studentswindow.alignTo(button, 'bl', [0, 0]);
        }
    }
});
