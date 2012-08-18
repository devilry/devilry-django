/** Assignment layout TODO-list. Reloads the TODO-list whenever it is shown (on
 * the show-event). */
Ext.define('devilry.examiner.AssignmentLayoutTodoList', {
    extend: 'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList',
    alias: 'widget.examiner-assignmentlayout-todolist',

    requires: [
        'devilry.extjshelpers.studentsmanager.StudentsManager',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList',
        'devilry.extjshelpers.charts.PointsOfGroupsOnSingleAssignment'
    ],

    /**
     * @cfg
     * Assignment ID to show todo items within (Required).
     */
    assignmentid: undefined,

    initComponent: function() {
        Ext.apply(this, {
            title: gettext('Todo-list'),
            toolbarExtra: ['->', {
                xtype: 'button',
                scale: 'large',
                iconCls: 'icon-save-32',
                text: interpolate(gettext('Download all %(deliveries_term)s'), {
                    deliveries_term: gettext('deliveries')
                }, true),
                listeners: {
                    scope: this,
                    click: this.onDownload
                }
            }],
            
            helpTpl: Ext.create('Ext.XTemplate',
                '<div class="section helpsection">',
                '   {todohelptext}',
                '   <p>Choose the <span class="menuref">Detailed overview of all students tab</span> to view all groups, and to give feedback in bulk.</p>',
                '   <p>You may want to <span class="menuref">Download all deliveries</span> as a zip file instead of downloading the delivery for each student/group separately. This will download all deliveries from all assignment groups where you are examiner on this assignment, not just the deliveries in your todo-list.</p>',
                '</div>'
            ),

            //onSelectGroup: function(grid, assignmentgroupRecord) {
                //var url = Ext.String.format('../assignmentgroup/{0}',
                    //assignmentgroupRecord.data.id
                //);
                //window.location.href = url;
            //},
            getGroupUrlPrefix: function() {
                return '../assignmentgroup/';
            }
        });
        this.on('show', this._loadTodoList);
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
