Ext.define('devilry.student.browseperiods.PeriodGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.student-browseperiods-periodgrid',
    
    constructor: function(config) {
        this.createStore();
        this.store.load();
        this.callParent([config]);
    },

    cellTpl: Ext.create('Ext.XTemplate',
        '{parentnode__short_name}.{short_name}'
    ),

    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.student.simplified.SimplifiedPeriod',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });
        this.store.proxy.setDevilryOrderby(['parentnode__short_name', '-start_time']);
        this.store.pageSize = 100000;
    },
    
    initComponent: function() {
        Ext.apply(this, {
            cls: 'selectable-grid',
            columns: [{
                header: 'Subject/course', dataIndex: 'parentnode__short_name', flex: 1,
                renderer: function(value, m, record) {
                    return this.cellTpl.apply(record.data);
                }
            }]
        });
        this.callParent(arguments);
    }
});
