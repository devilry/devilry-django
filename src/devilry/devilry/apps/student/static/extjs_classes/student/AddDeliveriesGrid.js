Ext.define('devilry.student.AddDeliveriesGrid', {
    extend: 'devilry.extjshelpers.DashGrid',

    requires: [
        'devilry.extjshelpers.DateTime'
    ],

    config: {
        store: undefined,
        model: undefined,
        noRecordsMessage: {
            title: 'No active electronic assignments',
            msg: "You are not expected to make any electronic deliveries at this time. This may be because none of your subjects/courses uses Devilry for electronic deliveries, or because all your published assignments have been corrected."
        },
        dashboard_url: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    createStore: function() {
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            "field": "is_open",
            "comp": "exact",
            "value": true
        }, {
            field: 'parentnode__delivery_types',
            comp: 'exact',
            value: 0 // ELECTRONIC deliveries
        }, {
            field: 'parentnode__parentnode__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'parentnode__parentnode__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-latest_deadline_deadline']);
    },

    createBody: function() {
        var rowTpl = Ext.create('Ext.XTemplate',
            '{.:date}'
        );

        var grid = Ext.create('Ext.grid.Panel', {
            frame: false,
            hideHeaders: true,
            frameHeader: false,
            autoScroll: true,
            flex: 1,
            border: false,
            sortableColumns: false,
            cls: 'selectable-grid',
            store: this.store,
        
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
                width: 180,
                dataIndex: 'latest_deadline_deadline',
                renderer: function(value, m, record) {
                    var rowTpl = Ext.create('Ext.XTemplate',
                        '<em style="font-style:italic">Deadline:</em> {latest_deadline_deadline}'
                    );
                    return rowTpl.apply(record.data);
                }
            },{
                text: '#Deliveries',
                menuDisabled: true,
                hideAble: false,
                width: 100,
                dataIndex: 'number_of_deliveries',
                renderer: function(value, m, record) {
                    var rowTpl = Ext.create('Ext.XTemplate',
                        '<em style="font-style:italic">Deliveries:</em> {number_of_deliveries}'
                    );
                    return rowTpl.apply(record.data);
                }
            }],
            listeners: {
                scope: this,
                itemmouseup: function(view, record) {
                    var url = this.dashboard_url + "add-delivery/" + record.data.id;
                    window.location = url;
                },
                itemmouseenter: function(view, record, item) {
                    //console.log(item);
                }
            }
        });
        this.add([{
            xtype: 'box',
            html: '<div class="section"><h3>Assignments / Add deliveries</h3></div>'
        }, grid]);
    }
});
