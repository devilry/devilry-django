Ext.define('devilry.extjshelpers.ActivePeriodsGrid', {
    extend: 'devilry.extjshelpers.DashGrid',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],

    config: {
        model: undefined,
        noRecordsMessage: {
            title: 'No active periods',
            msg: "You are not registered on any active periods/semesters. You can find inactive periods/semesters using the search box."
        },
        pageSize: 30,
        dashboard_url: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-publishing_time']);
        this.store.pageSize = this.pageSize
    },

    createBody: function() {
        var activePeriodsGrid = Ext.create('Ext.grid.Panel', {
            frame: false,
            frameHeader: false,
            border: false,
            sortableColumns: false,
            autoScroll: true,
            cls: 'selectable-grid',
            store: this.store,
            flex: 1,
            columns: [{
                text: 'Subject',
                menuDisabled: true,
                dataIndex: 'parentnode__long_name',
                flex: 30,
            },{
                text: 'Period',
                menuDisabled: true,
                dataIndex: 'long_name',
                flex: 20,
            }],
            listeners: {
                scope: this,
                itemmouseup: function(view, record) {
                    var url = this.dashboard_url + "period/" + record.data.id
                    window.location = url;
                }
            }
        });
        this.add({
            xtype: 'box',
            html: '<div class="section"><h2>Active periods/semesters</h2></div>'
        });
        this.add(activePeriodsGrid);
    }
});
