Ext.define('devilry.student.AddDeliveriesGrid', {
    extend: 'Ext.grid.Panel',
    frameHeader: false,
    frame: false,
    border: false,
    sortableColumns: false,
    columnLines: false,
    cls: 'selectable-grid',

    initComponent: function() {
        var rowTpl = Ext.create('Ext.XTemplate',
            '{.:date}'
        );
        Ext.apply(this, {
            columns: [{
                text: 'Subject',
                menuDisabled: true,
                hideable: false,
                dataIndex: 'assignment_group__parentnode__parentnode__parentnode__long_name',
                flex: 20
            },{
                text: 'Assignment',
                menuDisabled: true,
                hideable: false,
                flex: 15,
                dataIndex: 'assignment_group__parentnode__long_name'
            },{
                text: 'Deadline',
                menuDisabled: true,
                hideable: false,
                flex: 15,
                dataIndex: 'deadline',
                renderer: function(value) {
                    return rowTpl.apply(value);
                }
            },{
                text: '#Deliveries',
                menuDisabled: true,
                hideAble: false,
                flex: 5,
                dataIndex: 'number_of_deliveries'
            }],
            listeners: {
                scope: this,
                itemmouseup: function(view, record) {
                    var url = DASHBOARD_URL + "add-delivery/" + record.data.id;
                    window.location = url;
                },
                itemmouseenter: function(view, record, item) {
                    //console.log(item);
                }
            }
        });
        this.callParent(arguments);
    }
});
