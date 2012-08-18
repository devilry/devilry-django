Ext.define('devilry.examiner.ActiveAssignmentsView', {
    extend: 'devilry.extjshelpers.DashGrid',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],

    config: {
        model: undefined,
        noRecordsMessage: {
            title: 'No active assignments',
            msg: 'You are not registered on any assignments in an active period.'
        },
        pageSize: 30,
        dashboard_url: undefined
    },

    assignmentRowTpl: Ext.create('Ext.XTemplate',
        '<a href="{url}">',
            '{data.parentnode__parentnode__short_name}.',
            '{data.parentnode__short_name} - ',
            '{data.long_name}',
        '</a>'
    ),

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
        var me = this;
        var activeAssignmentsGrid = Ext.create('Ext.grid.Panel', {
            frame: false,
            frameHeader: false,
            border: false,
            sortableColumns: false,
            disableSelection: true,
            autoScroll: true,
            cls: 'bootstrap',
            store: this.store,
            flex: 1,
            hideHeaders: true,
            //features: [groupingFeature],
            columns: [{
                text: 'unused',
                menuDisabled: true,
                flex: 1,
                dataIndex: 'long_name',
                renderer: function(value, meta, record) {
                    console.log(record.data);
                    return me.assignmentRowTpl.apply({
                        data: record.data,
                        url: Ext.String.format('{0}assignment/{1}', me.dashboard_url, record.get('id'))
                    });
                }
            }]
        });
        this.add({
            xtype: 'box',
            html: '<div class="section"><h2>' + 'Assignments in an active period' + '</h2></div>'
        });
        this.add(activeAssignmentsGrid);
    }

});
