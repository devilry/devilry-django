/** Deadline listing.
 *
 * Lists {@link devilry.extjshelpers.assignmentgroup.DeadlineInfo}'s
 * within the given assignmentgroup ({@link #assignmentgroupid}).
 */
Ext.define('devilry.extjshelpers.assignmentgroup.DeadlineListing', {
    extend: 'Ext.container.Container',
    alias: 'widget.deadlinelisting',
    cls: 'widget-deadlinelisting',
    requires: [
        'devilry.extjshelpers.assignmentgroup.DeadlineInfo'
    ],

    config: {
        /**
        * @cfg
        * AssignmentGroup id.
        */
        assignmentgroupid: undefined,

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
        deadlinestore: undefined
    },

    initComponent: function() {
        this.callParent(arguments);
        this.loadDeadlines();
    },

    loadDeadlines: function() {
        this.deadlinestore.proxy.extraParams.orderby = Ext.JSON.encode(['-number']);
        this.deadlinestore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'assignment_group',
            comp: 'exact',
            value: this.assignmentgroupid
        }]);

        this.deadlinestore.load({
            scope: this,
            callback: this.onLoadDeadlines
        });
    },

    onLoadDeadlines:function(deadlinerecords) {
        var me = this;
        Ext.each(deadlinerecords, function(deadlinerecord) {
            me.addDeadline(deadlinerecord.data);
        });
    },

    addDeadline: function(deadline) {
        this.add({
            xtype: 'deadlineinfo',
            deadline: deadline,
            deliverymodel: this.deliverymodel
        });
    },

    selectDelivery: function(deliveryrecord) {
        Ext.each(this.items.items, function(deadlineinfo, index) {
            deadlineinfo.selectDelivery(deliveryrecord);
        });
    }
});
