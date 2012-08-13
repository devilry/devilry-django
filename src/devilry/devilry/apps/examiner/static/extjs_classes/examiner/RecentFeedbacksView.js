Ext.define('devilry.examiner.RecentFeedbacksView', {
    extend: 'devilry.extjshelpers.DashGrid',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],


    /**
     * @cfg {Object} [model]
     */

    /**
     * @cfg {int} [limit]
     */
    limit: 4,
    
    /**
     * @cfg {bool} [showStudentsCol]
     */
    showStudentsCol: true,

    /**
     * @cfg {Object} [noRecordsMessage]
     */
    noRecordsMessage: {
        title: gettext('No recent feedback'),
        msg: gettext("You are not registered on any assignment groups with recent feedback.")
    },


    studentsRowTpl: Ext.create('Ext.XTemplate',
        '<ul class="commaSeparatedList">',
        '   <tpl for="delivery__deadline__assignment_group__candidates__identifier">',
        '       <li>{.}</li>',
        '   </tpl>',
        '</ul>'
    ),

    assignmentRowTpl: Ext.create('Ext.XTemplate',
        '<a href="{url}">',
            '{data.delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.',
            '{data.delivery__deadline__assignment_group__parentnode__parentnode__short_name}.',
            '{data.delivery__deadline__assignment_group__parentnode__short_name}',
        '</a>'
    ),

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

        var urlCreateFunction = Ext.bind(this.urlCreateFn, this.urlCreateFnScope);
        var columns = [{
            text: 'Assignment',
            menuDisabled: true,
            flex: 30,
            dataIndex: 'id',
            renderer: function(value, meta, record) {
                return me.assignmentRowTpl.apply({
                    data: record.data,
                    url: urlCreateFunction(record)
                });
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
            disableSelection: true,
            frameHeader: false,
            autoScroll: true,
            flex: 1,
            border: false,
            sortableColumns: false,
            cls: 'bootstrap',
            store: this.store,
            columns: columns
        });
        this.add({
            xtype: 'box',
            tpl: '<div class="section"><h3>{text}</h3></div>',
            cls: 'bootstrap',
            data: {
                text: interpolate(gettext("Recent %(feedbacks)s"), {
                    feedbacks: gettext('feedbacks')
                }, true)
            }
        });
        this.add(activeAssignmentsGrid);
    }
});
