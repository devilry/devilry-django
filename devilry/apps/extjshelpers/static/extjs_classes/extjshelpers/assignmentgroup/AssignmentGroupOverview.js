/**
 *
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview', {
    extend: 'Ext.panel.Panel',
    width: 1000,
    height: 800,
    layout: 'border',
    alias: 'widget.assignmentgroupoverview',
    requires: [
        'devilry.extjshelpers.assignmentgroup.DeliveryInfo',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupDetailsPanel',
        'devilry.extjshelpers.assignmentgroup.DeadlineListing'
    ],

    headingTpl: Ext.create('Ext.XTemplate',
        '<div class="treeheader">',
        '   <div class="level1">{parentnode__parentnode__parentnode__long_name}</div>',
        '   <div class="level2">{parentnode__parentnode__long_name}</div>',
        '   <div class="level3">{parentnode__long_name}</div>',
        '<div>'
    ),

    config: {
        /**
         * @cfg
         * AssignmentGroup ``Ext.data.Store``. (Required).
         */
        assignmentgroupstore: undefined,

        /**
         * @cfg 
         * Delivery  ``Ext.data.Model``. (Required).
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
         * FileMeta ``Ext.data.Store``. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.DeliveryInfo}.
         */
        filemetastore: undefined,

        /**
         * @cfg
         * FileMeta ``Ext.data.Store``. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo}.
         */
        staticfeedbackstore: undefined,

        /**
         * @cfg
         * Enable creation of new feedbacks? Defaults to ``false``.
         * See: {@link devilry.extjshelpers.assignmentgroup.DeliveryInfo#canExamine}.
         *
         * When this is ``true``, the authenticated user still needs to have
         * permission to POST new feedbacks for the view to work.
         */
        canExamine: false
    },


    initComponent: function() {
        Ext.apply(this, {
            items: [{
                region: 'west',
                layout: 'fit',
                width: 220,
                xtype: 'panel',
                collapsible: true,   // make collapsible
                //titleCollapse: true, // click anywhere on title to collapse.
                split: true,
                items: [{
                    xtype: 'panel',
                    layout: 'border',
                    items: [{
                        region: 'north',
                        items: [{
                            xtype: 'assignmentgroupdetailspanel',
                            //title: 'Assignment group',
                            bodyPadding: 10,
                            singlerecordontainer: this.assignmentgroup_recordcontainer
                        }]
                    }, {
                        region: 'center',
                        items: [{
                            xtype: 'deadlinelisting',
                            title: 'Deadlines',
                            assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                            delivery_recordcontainer: this.delivery_recordcontainer,
                            deliverymodel: this.deliverymodel,
                            deadlinestore: this.deadlinestore,
                            selectedDeliveryId: this.selectedDeliveryId,
                            enableDeadlineCreation: this.canExamine
                        }]
                    }]
                }]
            }, {
                region: 'center',
                layout: 'border',
                items: [{
                    region: 'north',
                    xtype: 'deliveryinfo',
                    delivery_recordcontainer: this.delivery_recordcontainer,
                    filemetastore: this.filemetastore
                }, {
                    region: 'center',
                }]
            }],
        });
        this.callParent(arguments);
    }
});
