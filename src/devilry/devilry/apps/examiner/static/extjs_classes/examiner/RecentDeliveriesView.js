Ext.define('devilry.examiner.RecentDeliveriesView', {
    extend: 'devilry.extjshelpers.DashGrid',
    alias: 'widget.examiner_recentdeliveriesview',
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
        title: interpolate(gettext('No recent %(deliveries_term)s'), {
            deliveries_term: gettext('deliveries')
        }, true),
        msg: interpolate(gettext("You are not registered on any %(groups_term)s with recent %(deliveries_term)s."), {
            groups_term: gettext('groups'),
            deliveries_term: gettext('deliveries')
        }, true)
    },

    /**
     * @cfg {Function} [urlCreateFn]
     * Function to call to genereate urls. Takes a record of the given
     * ``model`` as argument.
     */

    /**
     * @cfg {Object} [urlCreateFnScope]
     * Scope of ``urlCreateFn``.
     */


    studentsRowTpl: Ext.create('Ext.XTemplate',
        '<ul class="commaSeparatedList">',
        '   <tpl for="deadline__assignment_group__candidates__identifier">',
        '       <li>{.}</li>',
        '   </tpl>',
        '</ul>'
    ),

    assignmentRowTpl: Ext.create('Ext.XTemplate',
        '<a href="{url}">',
            '{data.deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.',
            '{data.deadline__assignment_group__parentnode__parentnode__short_name}.',
            '{data.deadline__assignment_group__parentnode__short_name}',
        '</a>'
    ),

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
        }, {
            field: 'delivery_type',
            comp: 'exact',
            value: 0
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-time_of_delivery']);
        this.store.pageSize = this.limit;
    },

    createBody: function() {
        var me = this;

        var urlCreateFunction = Ext.bind(this.urlCreateFn, this.urlCreateFnScope);
        var columns = [{
            text: 'Assignment',
            menuDisabled: true,
            flex: 18,
            dataIndex: 'deadline__assignment_group__parentnode__long_name',
            renderer: function(value, meta, record) {
                return me.assignmentRowTpl.apply({
                    data: record.data,
                    url: urlCreateFunction(record)
                });
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
            cls: 'bootstrap',
            hideHeaders: true,
            frameHeader: false,
            disableSelection: true,
            border: false,
            sortableColumns: false,
            autoScroll: true,
            flex: 1,
            store: this.store,
            columns: columns
        });
        this.add({
            xtype: 'box',
            cls: 'bootstrap',
            tpl: '<div class="section"><h3>{text}</h3></div>',
            data: {
                text: interpolate(gettext('Recent %(deliveries)s'), {
                    deliveries: gettext('deliveries')
                }, true)
            }
        });
        this.add(activeAssignmentsGrid);
    }
});
