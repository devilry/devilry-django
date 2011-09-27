Ext.define('devilry.examiner.RecentDeliveriesView', {
    extend: 'devilry.extjshelpers.DashGrid',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],


    config: {
        model: undefined,
        limit: 4,
        showStudentsCol: true,
        noRecordsMessage: {
            title: 'No recent deliveries',
            msg: "You are not registered on any assignment groups with recent deliveries."
        },
        dashboard_url: undefined
    },

    studentsRowTpl: Ext.create('Ext.XTemplate',
        '<ul class="commaSeparatedList">',
        '   <tpl for="deadline__assignment_group__candidates__identifier">',
        '       <li>{.}</li>',
        '   </tpl>',
        '</ul>'
    ),

    assignmentRowTpl: Ext.create('Ext.XTemplate',
        '{deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.',
        '{deadline__assignment_group__parentnode__parentnode__short_name}.',
        '{deadline__assignment_group__parentnode__short_name}'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            groupField: 'deadline__assignment_group__parentnode__parentnode__parentnode__short_name',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'deadline__assignment_group__parentnode__parentnode__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'deadline__assignment_group__parentnode__parentnode__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-time_of_delivery']);
        this.store.pageSize = this.limit;
    },

    createBody: function() {
        var me = this;

        var columns = [{
            text: 'Assignment',
            menuDisabled: true,
            flex: 18,
            dataIndex: 'deadline__assignment_group__parentnode__long_name',
            renderer: function(value, meta, record) {
                return me.assignmentRowTpl.apply(record.data);
            }
        }, {
            text: 'Time of delivery',
            menuDisabled: true,
            width: 130,
            dataIndex: 'time_of_delivery',
            renderer: function(value) {
                var rowTpl = Ext.create('Ext.XTemplate',
                    '{.:date}'
                );
                return rowTpl.apply(value);
            }
        }];

        if(this.showStudentsCol) {
            Ext.Array.insert(columns, 1, [{
                text: 'Students',
                menuDisabled: true,
                dataIndex: 'id',
                flex: 20,
                renderer: function(value, meta, record) {
                    return me.studentsRowTpl.apply(record.data);
                }
            }]);
        };

        var activeAssignmentsGrid = Ext.create('Ext.grid.Panel', {
            frame: false,
            hideHeaders: true,
            frameHeader: false,
            border: false,
            sortableColumns: false,
            autoScroll: true,
            flex: 1,
            cls: 'selectable-grid',
            store: this.store,
            columns: columns,
            listeners: {
                scope: this,
                itemmouseup: function(view, record) {
                    var url = Ext.String.format(
                        "{0}assignmentgroup/{1}?deliveryid={2}",
                        this.dashboard_url,
                        record.data.deadline__assignment_group,
                        record.data.id
                    );
                    window.location = url;
                }
            }
        });
        this.add({
            xtype: 'box',
            html: '<div class="section"><h3>Recent deliveries</h3></div>'
        });
        this.add(activeAssignmentsGrid);
    }
});
