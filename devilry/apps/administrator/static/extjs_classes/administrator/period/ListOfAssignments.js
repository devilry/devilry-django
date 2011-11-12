Ext.define('devilry.administrator.period.ListOfAssignments', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.administrator-period-listofassignments',
    cls: 'selectable-grid',
    hideHeaders: true,

    config: {
        periodid: undefined
    },
    
    constructor: function(config) {
        this.callParent([config]);
    },

    _loadAssignments: function() {
        this.store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: this.periodid
        }]);
        this.store.proxy.setDevilryOrderby(['publishing_time']);
        this.store.load();
    },
    
    initComponent: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
            remoteFilter: true,
            remoteSort: true
        });
        this._loadAssignments();
        Ext.apply(this, {
            columns: [{
                header: 'Long name',  dataIndex: 'long_name', flex: 1
            }],
            dockedItems: [{
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: true
            }],
            listeners: {
                scope: this,
                select: this._onSelect
            }
        });
        this.callParent(arguments);
    },

    _onSelect: function(grid, record) {
        var url = Ext.String.format('{0}/administrator/assignment/{1}', DevilrySettings.DEVILRY_URLPATH_PREFIX, record.get('id'));
        window.location.href = url;
    }
});
