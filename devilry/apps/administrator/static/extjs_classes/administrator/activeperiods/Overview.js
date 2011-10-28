Ext.define('devilry.administrator.activeperiods.Overview', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.activeperiods-overview',
    frame: false,
    frameHeader: false,
    border: false,
    sortableColumns: false,
    autoScroll: true,
    cls: 'selectable-grid',

    requires: [
        'devilry.extjshelpers.DateTime'
    ],
    
    config: {
        node: undefined
    },
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.store.proxy.setDevilryFilters([{
            field: 'parentnode__parentnode',
            comp: 'exact',
            value: this.node.get('id')
        }, {
            field: 'start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.setDevilryOrderby(['-publishing_time']);
        this.store.pageSize = 100000;
        this.store.load();

        Ext.apply(this, {
            columns: [{
                text: 'Subject',
                menuDisabled: true,
                dataIndex: 'parentnode__long_name',
                flex: 30,
            },{
                text: 'Period',
                menuDisabled: true,
                dataIndex: 'long_name',
                flex: 20,
            }],
            listeners: {
                scope: this,
                itemmouseup: function(view, record) {
                    var url = Ext.String.format('{0}/statistics/admin/{1}?view=minimal', DevilrySettings.DEVILRY_URLPATH_PREFIX, record.data.id);
                    window.open(url, '_blank');
                }
            }
        });
        this.callParent(arguments);
    }
});
