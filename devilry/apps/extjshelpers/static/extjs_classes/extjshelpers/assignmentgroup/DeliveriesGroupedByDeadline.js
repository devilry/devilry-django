Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesGroupedByDeadline', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.deliveriesgroupedbydeadline',
    cls: 'widget-deliveriesgroupedbydeadline',
    requires: [
        'devilry.extjshelpers.RestFactory',
        'devilry.administrator.models.Delivery',
        'devilry.administrator.models.Deadline',
        'devilry.extjshelpers.assignmentgroup.DeliveriesGrid'
    ],

    title: 'Deliveries grouped by deadline',

    layout: {
        type: 'accordion'
    },
    height: 200,

    config: {
        assignmentgroup_recordcontainer: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.assignmentgroup_recordcontainer.on('setRecord', this.loadAllDeadlines, this);
    },

    titleTpl: Ext.create('Ext.XTemplate',
        '<div class="deadline_title">',
        '    <div>Deadline: <span class="deadline">{deadline:date}</span></div>',
        '    <div>',
        '        Deliveries: <span class="number_of_deliveries">{number_of_deliveries}</span>',
        '    </div>',
        '<div>'
    ),


    /**
     * @private
     */
    loadAllDeadlines: function() {
        var deadlinestore = devilry.extjshelpers.RestFactory.createStore('administrator', 'Deadline', {
            filters: [{
                property: 'assignment_group',
                value: this.assignmentgroup_recordcontainer.record.data.id
            }]
        });
        deadlinestore.proxy.setDevilryOrderby(['-deadline']);
        deadlinestore.loadAll({
            scope: this,
            callback: this.onLoadAllDeadlines
        });
    },

    /**
     * @private
     */
    onLoadAllDeadlines: function(deadlineRecords) {
        Ext.each(deadlineRecords, this.handleSingleDeadline, this);
    },

    /**
     * @private
     */
    handleSingleDeadline: function(deadlineRecord, index) {
        var deliveriesStore = deadlineRecord.deliveries();
        //deliveriesStore.pageSize = 1; // Uncomment to test paging
        deliveriesStore.load(function(deliveryRecords) {
            console.log(deadlineRecord.data.deadline, deliveryRecords.length);
        });
        this.add({
            xtype: 'panel',
            title: this.titleTpl.apply(deadlineRecord.data),
            layout: 'fit',
            border: false,
            items: [{
                xtype: 'deliveriesgrid',
                store: deliveriesStore
            }]
        })
    }
});
