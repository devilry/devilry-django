Ext.define('devilry.examiner.AssignmentView', {
    extend: 'Ext.Container',
    frame: false,
    border: false,

    requires: [
        'devilry.extjshelpers.studentsmanager.StudentsManager',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList',
        'devilry.extjshelpers.charts.PointsOfGroupsOnSingleAssignment'
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
            title: 'To-do list',
            tbarExtra: ['->', {
               xtype: 'button',
               scale: 'large',
               text: 'Complete students overview',
               menu: [],
               enableToggle: true,
               listeners: {
                   scope: this,
                   click: this.onStudents
               }
            }],

            onSelectGroup: function(grid, assignmentgroupRecord) {
                var url = Ext.String.format('../assignmentgroup/{0}',
                    assignmentgroupRecord.data.id
                );
                window.location.href = url;
            },
        });


        Ext.apply(this, {
            items: [this._todolist, {
                xtype: 'panel',
                title: 'Overview',
                margin: {
                    top: 30
                },
                layout: 'fit',
                height: 800,
                width: "100%",
                items: {
                    xtype: 'chart_pointsofgroupsonsingleassignment',
                    store: this.assignmentgroupGraphstore
                }
            }]
        });
        this.callParent(arguments);

        var assignmentmodel = Ext.ModelManager.getModel(this.assignmentmodelname);
        assignmentmodel.load(this.assignmentid, {
            scope: this,
            success: this.onLoadAssignmentSuccess,
            failure: this.onLoadAssignmentFailure
        });
        this.loadTodoList();


        this.assignmentgroupGraphstore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode',
            comp: 'exact',
            value: this.assignmentid
        }]);
        this.assignmentgroupGraphstore.load({
            callback: function(records) {
                //console.log(records[0].data);
            }
        });
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
            studentswindow.alignTo(button, 'br', [-studentswindow.width, 0]);
        }
    }
});
