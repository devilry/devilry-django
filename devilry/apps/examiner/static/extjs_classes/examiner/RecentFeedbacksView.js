Ext.define('devilry.examiner.RecentFeedbacksView', {
    extend: 'devilry.extjshelpers.DashGrid',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],


    config: {
        model: undefined,
        limit: 4,
        showStudentsCol: true,
        noRecordsMessage: {
            title: 'No recent feedback',
            msg: "You are not registered on any assignment groups with recent feedback."
        },
        dashboard_url: undefined
    },

    studentsRowTpl: Ext.create('Ext.XTemplate',
        '<ul class="useridlist">',
        '   <tpl for="delivery__deadline__assignment_group__candidates__identifier">',
        '       <li>{.}</li>',
        '   </tpl>',
        '</ul>'
    ),

    assignmentRowTpl: Ext.create('Ext.XTemplate',
        '{delivery__deadline__assignment_group__parentnode__parentnode__short_name}.',
        '{delivery__deadline__assignment_group__parentnode__short_name}'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            groupField: 'delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'delivery__deadline__assignment_group__parentnode__parentnode__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'delivery__deadline__assignment_group__parentnode__parentnode__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-save_timestamp']);
        this.store.pageSize = this.limit;
    },

    createBody: function() {
        var me = this;
        var groupingFeature = Ext.create('Ext.grid.feature.Grouping', {
            groupHeaderTpl: '{name:uppercase}',
        });

        var columns = [{
            text: 'Assignment',
            menuDisabled: true,
            flex: 30,
            dataIndex: 'id',
            renderer: function(value, meta, record) {
                return me.assignmentRowTpl.apply(record.data);
            }
        }, {
            text: 'Feedback save time',
            menuDisabled: true,
            width: 130,
            dataIndex: 'save_timestamp',
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
            autoScroll: true,
            flex: 1,
            border: false,
            sortableColumns: false,
            cls: 'selectable-grid',
            store: this.store,
            features: [groupingFeature],
            columns: columns,
            listeners: {
                scope: this,
                itemmouseup: function(view, record) {
                    var url = Ext.String.format(
                        "{0}assignmentgroup/{1}?deliveryid={2}",
                        this.dashboard_url,
                        record.data.delivery__deadline__assignment_group,
                        record.data.delivery
                    );
                    window.location = url;
                }
            }
        });
        this.add({
            xtype: 'box',
            html: '<div class="section"><h3>Recent feedback</h3></div>'
        });
        this.add(activeAssignmentsGrid);
    }
});
