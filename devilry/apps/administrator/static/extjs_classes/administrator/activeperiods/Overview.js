Ext.define('devilry.administrator.activeperiods.Overview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.activeperiods-overview',

    requires: [
        'devilry.extjshelpers.DateTime'
    ],
    
    config: {
        node: undefined
    },
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);

        this.periodstore = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
            remoteFilter: true,
            remoteSort: true
        });

        this.periodstore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode__parentnode',
            comp: 'exact',
            value: this.node.get('id')
        }, {
            field: 'parentnode__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'parentnode__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.periodstore.proxy.extraParams.orderby = Ext.JSON.encode(['-publishing_time']);
        this.periodstore.pageSize = this.pageSize
    },
    
    initComponent: function() {
        Ext.apply(this, {
        });
        this.callParent(arguments);
    }
});
