/** AssignmentGroup info.
 *
 * Lists {@link devilry.extjshelpers.assignmentgroup.DeadlineListing} and info
 * about the AssignmentGroup.
 *
 *      -----------------------
 *      |                     |
 *      | Deadlinelisting     |
 *      |    DeadlineInfo     |
 *      |        DeliveryGrid |
 *      |    DeadlineInfo     |
 *      |        DeliveryGrid |
 *      |                     |
 *      -----------------------
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo', {
    extend: 'Ext.container.Container',
    alias: 'widget.assignmentgroupinfo',
    cls: 'widget-assignmentgroupinfo',
    requires: [
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupDetailsPanel',
        'devilry.extjshelpers.assignmentgroup.DeadlineListing'
    ],

    config: {
        /**
        * @cfg
        * AssignmentGroup id. (Required).
        */
        assignmentgroupid: undefined,

        /**
         * @cfg
         * Delivery ``Ext.data.Model``. (Required).
         */
        deliverymodel: undefined,

        /**
         * @cfg
         * Deadline ``Ext.data.Store``. (Required).
         * _Note_ that ``deadlinestore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.DeadlineListing}.
         */
        deadlinestore: undefined
    },

    layout: 'border',

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                region: 'north',
                items: [{
                    xtype: 'assignmentgroupdetailspanel',
                }]
            }, {
                region: 'center',
                items: [{
                    xtype: 'deadlinelisting',
                    assignmentgroupid: this.assignmentgroupid,
                    deliverymodel: this.deliverymodel,
                    deadlinestore: this.deadlinestore
                }]
            }]
        });
        this.callParent(arguments);
    },
});
