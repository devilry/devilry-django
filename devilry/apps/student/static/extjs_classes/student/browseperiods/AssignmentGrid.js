Ext.define('devilry.student.browseperiods.AssignmentGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.student-browseperiods-assignmentgrid',
    
    constructor: function(config) {
        this.createStore();
        this.callParent([config]);
    },

    cellTpl: Ext.create('Ext.XTemplate',
        '{parentnode__long_name}'
    ),

    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.student.simplified.SimplifiedAssignmentGroup',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });
        this.store.pageSize = 100000;
        this.store.proxy.setDevilryOrderby(['parentnode__publishing_time', 'parentnode__short_name']);
    },

    loadGroupsInPeriod: function(periodRecord) {
        this.store.proxy.setDevilryFilters([{
            field: 'parentnode__parentnode',
            comp: 'exact',
            value: periodRecord.get('id')
        }])
        this.store.load();
    },
    
    initComponent: function() {
        Ext.apply(this, {
            cls: 'selectable-grid',
            hideHeaders: true,
            columns: [{
                header: 'Assignment', dataIndex: 'short_name', flex: 1,
                renderer: function(value, m, record) {
                    return this.cellTpl.apply(record.data);
                }
            }],

            listeners: {
                scope: this,
                select: this._onSelect
            }
        });
        this.callParent(arguments);
    },

    _onSelect: function(grid, record) {
        console.log(record.data);
    }
});
