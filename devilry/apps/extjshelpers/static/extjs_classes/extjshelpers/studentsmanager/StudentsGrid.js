Ext.define('devilry.extjshelpers.studentsmanager.StudentsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.studentsmanager_studentsgrid',

    config: {
        assignmentid: undefined
    },

    columns: [
        {header: 'Students', dataIndex: 'id', flex: 2},
        {header: 'Examiners', dataIndex: 'id', flex: 2},
        {header: 'Points', dataIndex: 'feedback__points', flex: 3}
    ],

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.store.pageSize = 10;
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode',
            comp: 'exact',
            value: this.assignmentid
        }]);
        Ext.apply(this, {
            dockedItems: [{
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: true
            }]
        });
        this.callParent(arguments);
        this.store.load({
            params: {
                start: 0,
                limit: 10
            }
        });
    }
});
