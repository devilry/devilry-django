Ext.define('devilry.examiner.ActiveAssignmentsView', {
    extend: 'devilry.extjshelpers.DashGrid',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],

    noRecordsMessage: {
        title: 'No active assignments',
        msg: "You are not examiner on any assignments in an active period/semester. You can find inactive assignments using the search box."
    },
    
    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            groupField: 'parentnode__parentnode__long_name',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.model.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'parentnode__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
    },

    createBody: function() {
        var groupingFeature = Ext.create('Ext.grid.feature.Grouping', {
            groupHeaderTpl: '{name}',
        });
        var activeAssignmentsGrid = Ext.create('Ext.grid.Panel', {
            frame: false,
            frameHeader: false,
            border: false,
            sortableColumns: false,
            cls: 'selectable-grid',
            store: this.store,
            features: [groupingFeature],
            columns: [{
                text: 'Assignment',
                menuDisabled: true,
                flex: 30,
                dataIndex: 'long_name'
            },{
                text: 'Period',
                menuDisabled: true,
                dataIndex: 'parentnode__long_name',
                flex: 20,
            },{
                text: 'Published',
                menuDisabled: true,
                flex: 15,
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
                    var url = DASHBOARD_URL + "assignment/" + record.data.id
                    window.location = url;
                }
            }
        });
        this.add({
            xtype: 'box',
            html: '<h1>Assignments</h1>'
        })
        this.add(activeAssignmentsGrid);
    }

});
