Ext.define('devilry.examiner.ActiveAssignmentsView', {
    extend: 'devilry.extjshelpers.DashGrid',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],

    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    config: {
        model: undefined,
        noRecordsMessage: {
            title: 'No active assignments',
            msg: "You are not registered on any assignments in an active period/semester. You can find inactive assignments using the search box."
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
            //groupField: 'parentnode__parentnode__long_name',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'parentnode__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-publishing_time']);
        this.store.pageSize = this.pageSize
    },

    createBody: function() {
        //var groupingFeature = Ext.create('Ext.grid.feature.Grouping', {
            //groupHeaderTpl: '{name}',
        //});
        var activeAssignmentsGrid = Ext.create('Ext.grid.Panel', {
            frame: false,
            frameHeader: false,
            border: false,
            sortableColumns: false,
            autoScroll: true,
            cls: 'selectable-grid',
            store: this.store,
            flex: 1,
            //features: [groupingFeature],
            columns: [{
                text: 'Subject',
                menuDisabled: true,
                dataIndex: 'parentnode__parentnode__long_name',
                flex: 20,
            },{
                text: 'Period',
                menuDisabled: true,
                dataIndex: 'parentnode__long_name',
                flex: 20,
            },{
                text: 'Assignment',
                menuDisabled: true,
                flex: 20,
                dataIndex: 'long_name'
            },{
                text: 'Published',
                menuDisabled: true,
                width: 150,
                dataIndex: 'publishing_time',
                renderer: function(value) {
                    var rowTpl = Ext.create('Ext.XTemplate',
                        '{.:date}'
                    );
                    return rowTpl.apply(value);
                }
            }],
            listeners: {
                scope: this,
                itemmouseup: function(view, record) {
                    var url = this.dashboard_url + "assignment/" + record.data.id
                    window.location = url;
                }
            }
        });
        this.add({
            xtype: 'box',
            html: '<div class="section"><h2>Assignments in an active period/semester</h2></div>'
        });
        this.add(activeAssignmentsGrid);
    }

});
