/** AssignmentGroup info.
 *
 * Lists DeadlineListing and info about the AssignmentGroup.
 *
 * @xtype assignmentgroupinfo
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo', {
    extend: 'Ext.container.Container',
    alias: 'widget.assignmentgroupinfo',
    cls: 'widget-assignmentgroupinfo',
    requires: [
        'devilry.extjshelpers.assignmentgroup.DeadlineListing'
    ],

    config: {
        /**
        * @cfg
        * AssignmentGroup id.
        */
        assignmentgroupid: undefined,

        /**
         * @cfg {Ext.data.Model} Delivery model.
         */
        deliverymodel: undefined
    },

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'deadlinelisting',
                assignmentgroupid: this.assignmentgroupid,
                deliverymodel: this.deliverymodel
            }]
        });
        this.callParent(arguments);
    },
});
