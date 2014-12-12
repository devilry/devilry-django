Ext.define('devilry.extjshelpers.ActivePeriodsGrid', {
    extend: 'devilry.extjshelpers.DashGrid',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],

    config: {
        model: undefined,
        noRecordsMessage: {
            title: interpolate(gettext('No active %(periods_term)s'), {
                periods_term: gettext('periods')
            }, true),
            msg: interpolate(gettext('You are not registered on any active %(periods_term)s.'), {
                periods_term: gettext('periods')
            }, true)
        },
        pageSize: 30,
        dashboard_url: undefined
    },

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
            field: 'start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-publishing_time']);
        this.store.pageSize = this.pageSize
    },

    createBody: function() {
        var colTpl = Ext.create('Ext.XTemplate',
            '<a href="{dashboard_url}period/{data.id}">',
                '{data.parentnode__short_name} - {data.long_name}',
            '</a>'
        );
        var me = this;
        var activePeriodsGrid = Ext.create('Ext.grid.Panel', {
            frame: false,
            frameHeader: false,
            border: false,
            cls: 'bootstrap',
            sortableColumns: false,
            autoScroll: true,
            store: this.store,
            hideHeaders: true,
            flex: 1,
            columns: [{
                text: 'unused',
                menuDisabled: true,
                dataIndex: 'id',
                flex: 1,
                renderer: function(unused, unused2, periodRecord) {
                    return colTpl.apply({
                        data: periodRecord.data,
                        dashboard_url: me.dashboard_url
                    });
                }
            }]
            //listeners: {
                //scope: this,
                //itemmouseup: function(view, record) {
                    //var url = this.dashboard_url + "period/" + record.data.id
                    //window.location = url;
                //}
            //}
        });
        this.add({
            xtype: 'box',
            html: Ext.String.format('<div class="section"><h2>{0}</h2></div>',
                interpolate(gettext('Active %(periods_term)s'), {
                    periods_term: gettext('periods')
                }, true)
            )
        });
        this.add(activePeriodsGrid);
    }
});
