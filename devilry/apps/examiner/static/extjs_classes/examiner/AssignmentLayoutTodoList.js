Ext.define('devilry.examiner.AssignmentLayoutTodoList', {
    extend: 'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList',
    alias: 'widget.examiner-assignmentlayout-todolist',

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
        Ext.apply(this, {
            title: 'Todo-list',
            store: this.assignmentgroupstore,
            toolbarExtra: ['->', {
               xtype: 'button',
               scale: 'large',
               iconCls: 'icon-save-32',
               text: 'Download all deliveries',
               listeners: {
                   scope: this,
                   click: this.onDownload
               }
            }],
            listeners: {
                scope: this,
                show: function() {
                    this._loadTodoList();
                }
            },
            
            helpTpl: Ext.create('Ext.XTemplate',
                '<div class="section helpsection">',
                '   {todohelptext}',
                '   <p>Choose the <span class="menuref">Detailed overview of all students tab</span> to view all groups, and to give feedback in bulk.</p>',
                '   <p>You may want to <span class="menuref">Download all deliveries</span> as a zip file instead of downloading the delivery for each student/group separately. This will download all deliveries from all assignment groups where you are examiner on this assignment, not just the deliveries in your todo-list.</p>',
                '</div>'
            ),

            onSelectGroup: function(grid, assignmentgroupRecord) {
                var url = Ext.String.format('../assignmentgroup/{0}',
                    assignmentgroupRecord.data.id
                );
                window.location.href = url;
            },
        });
        this.callParent(arguments);
        this._loadTodoList();
    },


    _loadTodoList: function() {
        this.loadTodoListForAssignment(this.assignmentid);
    },

    onDownload: function() {
        window.location.href = Ext.String.format('compressedfiledownload/{0}', this.assignmentid);
    }
});
