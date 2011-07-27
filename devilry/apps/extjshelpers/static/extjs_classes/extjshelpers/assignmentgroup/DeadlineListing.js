/** Deadline listing.
 *
 * Lists {@link devilry.extjshelpers.assignmentgroup.DeadlineInfo}'s
 * within the given assignmentgroup ({@link #assignmentgroup_recordcontainer}).
 */
Ext.define('devilry.extjshelpers.assignmentgroup.DeadlineListing', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.deadlinelisting',
    cls: 'widget-deadlinelisting',
    requires: [
        'devilry.extjshelpers.assignmentgroup.DeadlineInfo'
    ],

    config: {
        /**
         * @cfg
         * Delivery ``Ext.data.Model``.
         */
        deliverymodel: undefined,

        /**
         * @cfg
         * Deadline ``Ext.data.Store``. (Required).
         * _Note_ that ``deadlinestore.proxy.extraParams`` is changed by
         * this class.
         */
        deadlinestore: undefined,

        /**
         * @cfg
         * Viewable buttons depends on this
         * 
         */
        canExamine: false,

        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
         * The record is changed when a user selects a delivery.
         */
        delivery_recordcontainer: undefined
    },

    constructor: function(config) {
        this.addEvents(
            /**
             * @event
             * Fired when a delivery is selected.
             * @param deliveryRecord The selected delivery record.
             */
            'selectDelivery');
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        if (this.canExamine)
        {
            Ext.apply(this, {
                tbar: [
                {
                    xtype: 'button',
                    text: 'Create new deadline',
                    iconCls: 'icon-add-16',
                    listeners: {
                        click: function ()
                        {
                            console.log('TODO');
                        }
                    }
                }]
            });
        }
        this.callParent(arguments);
        this.assignmentgroup_recordcontainer.addListener('setRecord', this.reload, this);
        this.addListener('selectDelivery', this.onSelectDelivery, this);
    },

    /** Reload all deadlines on this assignmentgroup. */
    reload: function() {
        this.removeAll();
        this.loadDeadlines(this.assignmentgroup_recordcontainer.record.data.id);
    },

    /**
     * @private
     */
    onSelectDelivery: function(deliveryRecord) {
        //console.log(deliveryRecord);
        this.delivery_recordcontainer.setRecord(deliveryRecord);
    },

    /**
     * @private
     */
    loadDeadlines: function(assignmentgroupid) {
        this.deadlinestore.proxy.extraParams.orderby = Ext.JSON.encode(['-number']);
        this.deadlinestore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'assignment_group',
            comp: 'exact',
            value: assignmentgroupid
        }]);

        this.deadlinestore.load({
            scope: this,
            callback: this.onLoadDeadlines
        });
    },

    /**
     * @private
     */
    onLoadDeadlines:function(deadlinerecords) {
        var me = this;
        Ext.each(deadlinerecords, function(deadlinerecord) {
            me.addDeadline(deadlinerecord.data);
        });
    },

    /**
     * @private
     */
    addDeadline: function(deadline) {
        this.add({
            xtype: 'deadlineinfo',
            deadline: deadline,
            deliverymodel: this.deliverymodel,
            delivery_recordcontainer: this.delivery_recordcontainer
        });
    },
});
