Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoListWindow', {
    extend: 'Ext.window.Window',
    title: gettext('To-do list (Open groups on this assignment)'),
    height: 370,
    width: 750,
    modal: true,
    layout: 'fit',
    requires: [
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList'
    ],

    /**
     * @cfg
     */
    assignmentgroupmodelname: undefined,

    /**
     * @cfg
     */
    assignmentgroup_recordcontainer: undefined,

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'assignmentgrouptodolist',
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                assignmentgroupmodelname: this.assignmentgroupmodelname
            }
        });
        this.callParent(arguments);
    }
});
