Ext.define('devilry.student.AddDeliveriesGrid', {
    extend: 'devilry.extjshelpers.DashGrid',
    alias: 'widget.student-add-deliveriesgrid',

    requires: [
        'devilry.extjshelpers.DateTime',
        'Ext.XTemplate'
    ],

    /**
     * @cfg {Object} [store]
     */

    /**
     * @cfg {Object} [model]
     */

    /**
     * @cfg {Object} [noRecordsMessage]
     */
    noRecordsMessage: {
        title: interpolate(gettext('No active electronic %(assignments)s'), {
            assignments: gettext('assignments')
        }, true),
        msg: interpolate(gettext("You are not expected to make any electronic deliveries at this time. This may be because none of your %(subjects)s uses Devilry for electronic deliveries, or because all your published %(assignments)s have been corrected."), {
            subjects: gettext('subjects'),
            assignments: gettext('assignments')
        }, true)
    },


    /**
     * @cfg {Function} [urlCreateFn]
     * Function to call to genereate urls. Takes a record of the given ``model`` as argument.
     */

    /**
     * @cfg {Object} [urlCreateFnScope]
     * Scope of ``urlCreateFn``.
     */

    createStore: function() {
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            "field": "is_open",
            "comp": "exact",
            "value": true
        }, {
            field: 'parentnode__delivery_types',
            comp: 'exact',
            value: 0 // ELECTRONIC deliveries
        }, {
            field: 'parentnode__parentnode__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'parentnode__parentnode__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-latest_deadline_deadline']);
    },

    createBody: function() {
        var rowTpl = Ext.create('Ext.XTemplate',
            '{.:date}'
        );
        var nametpl = Ext.create('Ext.XTemplate',
            '<a href="{url}">',
                '{data.parentnode__parentnode__parentnode__short_name} - {data.parentnode__long_name}',
            '</a>'
        );

        var me = this;
        var urlCreateFunction = Ext.bind(this.urlCreateFn, this.urlCreateFnScope);
        var grid = Ext.create('Ext.grid.Panel', {
            frame: false,
            hideHeaders: true,
            frameHeader: false,
            disableSelection: true,
            autoScroll: true,
            flex: 1,
            border: false,
            sortableColumns: false,
            //cls: 'selectable-grid',
            store: this.store,
            cls: 'bootstrap',
        
            columns: [{
                text: 'Subject',
                menuDisabled: true,
                hideable: false,
                dataIndex: 'parentnode__parentnode__parentnode__long_name',
                flex: 20,
                renderer: function(unused, unused2, record) {
                    return nametpl.apply({
                        data: record.data,
                        url: urlCreateFunction(record)
                    });
                }
            },{
                text: 'Deadline',
                menuDisabled: true,
                hideable: false,
                width: 200,
                dataIndex: 'latest_deadline_deadline',
                renderer: function(value, m, record) {
                    var rowTpl = Ext.create('Ext.XTemplate',
                        '<em style="font-style:italic">{deadline}:</em> {record.latest_deadline_deadline}'
                    );
                    return rowTpl.apply({
                        deadline: gettext('Deadline'),
                        record: record.data
                    });
                }
            },{
                text: 'Deliveries',
                menuDisabled: true,
                hideAble: false,
                width: 120,
                dataIndex: 'number_of_deliveries',
                renderer: function(value, m, record) {
                    var rowTpl = Ext.create('Ext.XTemplate',
                        '<em style="font-style:italic">{deliveries}:</em> {record.number_of_deliveries}'
                    );
                    return rowTpl.apply({
                        record: record.data,
                        deliveries: gettext('Deliveries')
                    });
                }
            }]
        });
        this.add([{
            xtype: 'box',
            cls: 'bootstrap',
            tpl: '<div class="section"><h2>{text}</h2></div>',
            data: {
                text: interpolate(gettext('%(assignments)s / Add %(deliveries)s'), {
                    assignments: gettext('Assignments'),
                    deliveries: gettext('deliveries')
                }, true)
            }
        }, grid]);
    }
});
