/** Grid panel for showing deliveries within a deadline.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.DeliveryGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deliverygrid',
    cls: 'widget-deliverygrid',
    hideHeaders: true, // Hide column header

    rowTpl: Ext.create('Ext.XTemplate',
        '{number}. {time_of_delivery:date} (id:{id})'
    ),

    // TODO: Paging (In case we get more deliveries than the pageSize)

    columns: [{
        header: 'Data',
        dataIndex: 'id',
        flex: 1,
        renderer: function(value, metaData, deliveryrecord) {
            return this.rowTpl.apply(deliveryrecord.data);
        }
    }],

    listeners: {
        selectionchange: function(grid, selections) {
            var deliveryRecord = selections[0];
            this.up('deadlinelisting').fireEvent('selectDelivery', deliveryRecord);
        }
    },
});
