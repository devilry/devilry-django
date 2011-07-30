Ext.define('devilry.extjshelpers.assignmentgroup.DeadlinesOnSingleGroupManager', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.deadlinesonsinglegroupmanager',
    cls: 'widget-deadlinesonsinglegroupmanager',
    requires: [
        'devilry.extjshelpers.forms.Deadline',
        'devilry.extjshelpers.assignmentgroup.DeliveriesOnSingleGroupListing',
        'devilry.extjshelpers.assignmentgroup.DeadlinesOnSingleGroupListing'
    ],

    config: {
        /**
         * @cfg
         * Delivery ``Ext.data.Model``.
         */
        deliverymodel: undefined,

        /**
         * @cfg
         * Deadline ``Ext.data.Model``.
         */
        deadlinemodel: undefined,

        /**
         * @cfg
         * Deadline ``Ext.data.Store``.
         */

        /**
         * @cfg
         * Enable creation of new deadlines?
         */
        enableDeadlineCreation: false,

        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
         * The record is changed when a user selects a delivery.
         */
        delivery_recordcontainer: undefined,

        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for AssignmentGroup.
         */
        assignmentgroup_recordcontainer: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            //frame: false,
            //border: 0,
            items: [{
                title: 'Deliveries grouped by deadline',
                xtype: 'deliveriesonsinglegrouplisting',
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                delivery_recordcontainer: this.delivery_recordcontainer,
                deliverymodel: this.deliverymodel
            }, {
                title: 'Deadline overview',
                xtype: 'deadlinesonsinglegrouplisting',
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                deadlinemodel: this.deadlinemodel,
                enableDeadlineCreation: this.enableDeadlineCreation
            }]
        });
        this.callParent(arguments);
    }
});
