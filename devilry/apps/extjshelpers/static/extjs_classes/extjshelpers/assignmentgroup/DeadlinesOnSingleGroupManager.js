Ext.define('devilry.extjshelpers.assignmentgroup.DeadlinesOnSingleGroupManager', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.deadlinesonsinglegroupmanager',
    cls: 'widget-deadlinesonsinglegroupmanager',
    requires: [
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
        if(this.enableDeadlineCreation) {
            this.addCreateNewDeadlineButton();
        }

        Ext.apply(this, {
            layout: 'fit',
            //frame: false,
            //border: 0,
            items: [{
                title: 'Deliveries grouped by deadline',
                xtype: 'deliveriesonsinglegrouplisting',
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                delivery_recordcontainer: this.delivery_recordcontainer,
                deliverymodel: this.deliverymodel,
                deadlinemodel: this.deadlinemodel,
                enableDeadlineCreation: this.enableDeadlineCreation
            }, {
                title: 'Deadline overview',
                xtype: 'deadlinesonsinglegrouplisting',
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                deadlinemodel: this.deadlinemodel
            }]
        });
        this.callParent(arguments);
    },

    /**
     * @private
     * */
    addCreateNewDeadlineButton: function() {
        Ext.apply(this, {
            bbar: ['->', {
                xtype: 'button',
                text: 'Create new deadline',
                iconCls: 'icon-add-32',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this.onCreateNewDeadline
                }
            }]
        });
    },

    /**
     * @private
     */
    onCreateNewDeadline: function() {
        var createDeadlineWindow = Ext.create('devilry.extjshelpers.RestfulSimplifiedEditWindowBase', {
            title: 'Create deadline',
            editpanel: Ext.ComponentManager.create({
                xtype: 'restfulsimplified_editpanel',
                modelname: this.deadlinemodel,
                editformitems: assignmentgroupoverview_deadline_editformitems,
                foreignkeyfieldnames: assignmentgroupoverview_deadline_foreignkeyfieldnames
            }),
            onSaveSuccess: function(record) {
                this.close();
            }
        });
        createDeadlineWindow.show();
    }
});
