/** Grid panel for showing deliveries.
 *
 * @xtype deliverygrid
 */
Ext.define('devilry.extjshelpers.DeliveryGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deliverygrid',
    cls: 'widget-deliverygrid',
    hideHeaders: true, // Hide column header

    rowTpl: Ext.create('Ext.XTemplate',
        '{number}. {time_of_delivery:date} (id:{id})'
    ),

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
            var selectedDelivery = selections[0];
            this.up('assignmentgroupoverview').setDelivery(selectedDelivery);
        }
    }
});
