/** AssignmentGroup info.
 *
 * Lists {@link devilry.extjshelpers.assignmentgroup.DeadlineListing} and info
 * about the AssignmentGroup.
 *
 *      -------------------------------
 *      | AssignmentGroupDetailsPanel |
 *      |                             |
 *      | Deadlinelisting             |
 *      |    DeadlineInfo             |
 *      |        DeliveryGrid         |
 *      |    DeadlineInfo             |
 *      |        DeliveryGrid         |
 *      |                             |
 *      -------------------------------
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
        * AssignmentGroup object such as the ``data`` attribute of a record
        * returned from loading from a store. (Required).
        */
        assignmentgroup: undefined,

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
        deadlinestore: undefined,

        /**
         * @cfg
         * Selected delivery id. May be undefined, in which case, no delivery
         * is selected.
         */
        selectedDeliveryId: undefined
    },

    layout: 'border',

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                region: 'north',
                items: [{
                    xtype: 'assignmentgroupdetailspanel',
                    assignmentgroup: this.assignmentgroup,
                    bodyPadding: 10
                }]
            }, {
                region: 'center',
                items: [{
                    xtype: 'deadlinelisting',
                    title: 'Deadlines',
                    assignmentgroupid: this.assignmentgroup.id,
                    deliverymodel: this.deliverymodel,
                    deadlinestore: this.deadlinestore,
                    selectedDeliveryId: this.selectedDeliveryId
                }]
            }]
        });
        this.callParent(arguments);
    },
});
