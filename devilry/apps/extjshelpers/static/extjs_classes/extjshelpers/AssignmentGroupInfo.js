/** AssignmentGroup info.
 *
 * Lists DeadlineInfo and info about the AssignmentGroup.
 *
 * @xtype assignmentgroupinfo
 */
Ext.define('devilry.extjshelpers.AssignmentGroupInfo', {
    extend: 'Ext.container.Container',
    alias: 'widget.assignmentgroupinfo',
    cls: 'widget-assignmentgroupinfo',
    requires: [
        'devilry.extjshelpers.DeadlineListing'
    ],

    config: {
        assignmentgroupid: undefined
    },

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'deadlinelisting',
                assignmentgroupid: this.assignmentgroupid
            }]
        });
        this.callParent(arguments);
    },
});
