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

        //this.store.proxy.extraParams.orderby = Ext.JSON.encode(["deadline"]);
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            "field": "is_open",
            "comp": "exact",
            "value": true
        }, {
            field: 'parentnode__delivery_types',
            comp: 'exact',
            value: 0 // ELECTRONIC deliveries
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-latest_deadline_deadline']);
        this.store.load();

        Ext.apply(this, {
            columns: [{
                text: 'Subject',
                menuDisabled: true,
                hideable: false,
                dataIndex: 'parentnode__parentnode__parentnode__long_name',
                flex: 20
            },{
                text: 'Assignment',
                menuDisabled: true,
                hideable: false,
                flex: 15,
                dataIndex: 'parentnode__long_name'
            },{
                text: 'Deadline',
                menuDisabled: true,
                hideable: false,
                flex: 15,
                dataIndex: 'latest_deadline_deadline',
                renderer: function(value, m, record) {
                    try {
                        var rowTpl = Ext.create('Ext.XTemplate',
                            '{latest_deadline_deadline:date}'
                        );
                        return rowTpl.apply(record.data);
                    } catch(e) {
                        var rowTpl = Ext.create('Ext.XTemplate',
                            '{latest_deadline_deadline}'
                        );
                        return rowTpl.apply(record.data);
                    }
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
