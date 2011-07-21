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
        * AssignmentGroup id. (Required).
        */
        assignmentgroupid: undefined,

        /**
         * @cfg {Ext.data.Model} Delivery model. (Required).
         */
        deliverymodel: undefined,

        /**
         * @cfg {Ext.data.Store} Deadline store. (Required).
         * _Note_ that ``deadlinestore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.DeadlineListing}.
         */
        deadlinestore: undefined
    },

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'deadlinelisting',
                assignmentgroupid: this.assignmentgroupid,
                deliverymodel: this.deliverymodel,
                deadlinestore: this.deadlinestore
            }]
        });
        this.callParent(arguments);
    },
});
