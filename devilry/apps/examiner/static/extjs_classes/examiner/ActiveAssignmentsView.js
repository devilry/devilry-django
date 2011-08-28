Ext.define('devilry.examiner.ActiveAssignmentsView', {
    extend: 'Ext.Container',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],
    
    initComponent: function() {
        this.callParent(arguments);
        this.createStore();
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

        this.store.load({
            scope: this,
            callback: function(records, operation, success) {
                if(!success || records.length === 0) {
                    var args = {};
                    if(success) {
                        args = {
                            title: 'No active assignments',
                            msg: "You are not examiner on any assignments in an active period/semester. You can find inactive assignments using the search box.",
                            msgcls: 'info'
                        }
                    } else {
                        args = {
                            title: 'Error',
                            msg: "Failed to load assignments. Try re-loading the page.",
                            msgcls: 'error'
                        }
                    }
                    Ext.widget('box', {
                        renderTo: 'no-active-assignments-message',
                        html: Ext.create('Ext.XTemplate',
                            '<section class="{msgcls}-small extravisible-small">',
                            '   <h1>{title}</h1>',
                            '   <p>{msg}</p>',
                            '</section>'
                        ).apply(args)
                    });
                } else {
                    this.createGrid();
                }
            }
        });
    },

    createGrid: function() {
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
