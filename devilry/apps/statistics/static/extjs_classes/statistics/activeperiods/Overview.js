Ext.define('devilry.statistics.activeperiods.Overview', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.activeperiods-overview',
    frame: false,
    border: false,
    autoScroll: true,
    cls: 'selectable-grid',

    requires: [
        'devilry.extjshelpers.DateTime',
        'devilry.statistics.activeperiods.AggregatedPeriodModel',
        'devilry.extjshelpers.RestProxy',
        'devilry.extjshelpers.SearchField'
    ],
    
    config: {
        node: undefined
    },

    readyForExportTpl: Ext.create('Ext.XTemplate',
        '<tpl if="qualifies_for_exam_ready_for_export"><span class="goodInlineItem">yes</span></tpl>',
        '<tpl if="!qualifies_for_exam_ready_for_export"><span class="warningInlineItem">no</span></tpl>'
    ),
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this._createStore();
        this._createAndLoadPeriodStore();
        Ext.apply(this, {
            tbar: [
                //xtype: 'searchfield',
                //searchdelay: 30,
                //emptyText: 'Search...',
                //width: 200,
                //listeners: {
                    //scope: this,
                    //newSearchValue: this._onNewSearchValue,
                    //emptyInput: this._onEmptySearchValue
                //}
            //{
                //xtype: 'button',
                //text: 'Send email to admin(s) on visible',
                //listeners: {
                    //scope: this,
                    //click: this._sendEmailsToVisible
                //}
            '->', {
                xtype: 'combobox',
                width: 350,
                valueField: 'filterfunc',
                displayField: 'label',
                forceSelection: true,
                editable: false,
                emptyText: 'Show all',
                store: Ext.create('Ext.data.Store', {
                    fields: ['filterfunc', 'label'],
                    data: [{
                        filterfunc: this._clearFilters,
                        label: 'Show all'
                    }, {
                        filterfunc: this._filterQualifiesForExamYes,
                        label: 'Show qualifies-for-exam ready for export'
                    }, {
                        filterfunc: this._filterQualifiesForExamNo,
                        label: 'Show qualifies-for-exam NOT ready for export'
                    }],
                    proxy: 'memory'
                }),
                listeners: {
                    scope: this,
                    select: function(combo, records) {
                        var record = records[0];
                        var filterfunc = record.get('filterfunc');
                        Ext.bind(filterfunc, this)();
                    }
                }
            }],
            columns: [{
                text: 'Subject',
                dataIndex: 'subject_long_name',
                flex: 30
            },{
                text: 'Period',
                dataIndex: 'period_long_name',
                flex: 20
            },{
                text: '&laquo;Qualifies for exam&raquo; ready for export?',
                dataIndex: 'qualifies_for_exam_ready_for_export',
                flex: 20,
                renderer: function(value, m, record) {
                    return this.readyForExportTpl.apply(record.data);
                }
            }],
            listeners: {
                scope: this,
                itemmouseup: function(view, record) {
                    //var url = Ext.String.format('{0}/statistics/admin/{1}?view=minimal', DevilrySettings.DEVILRY_URLPATH_PREFIX, record.get('period_id'));
                    var url = Ext.String.format('{0}/administrator/period/{1}', DevilrySettings.DEVILRY_URLPATH_PREFIX, record.get('period_id'));
                    window.open(url, '_blank');
                }
            }
        });
        this.callParent(arguments);
    },


    _filterQualifiesForExamYes: function() {
        this.store.filterBy(function(record) {
            return record.get('qualifies_for_exam_ready_for_export') !== null;
        });
    },
    _filterQualifiesForExamNo: function() {
        this.store.filterBy(function(record) {
            return record.get('qualifies_for_exam_ready_for_export') === null;
        });
    },
    _clearFilters: function() {
        this.store.clearFilter();
    },

    //_onNewSearchValue: function(value) {
        //console.log(value);
    //},

    //_onEmptySearchValue: function() {
    //},


    _createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.statistics.activeperiods.AggregatedPeriodModel',
            autoSync: false,
            proxy: 'memory'
        });
    },

    _createAndLoadPeriodStore: function() {
        this.periodstore = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.periodstore.proxy.setDevilryFilters([{
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
        this.periodstore.proxy.setDevilryOrderby(['-publishing_time']);
        this.periodstore.pageSize = 100000;
        this.periodstore.load({
            scope: this,
            callback: this._onPeriodStoreLoad
        });
    },

    _onPeriodStoreLoad: function(records, op) {
        if(!op.success) {
            this._handleLoadError(op, 'Failed to load active periods.');
        } else {
            this._createAndLoadPeriodAppKeyValueStore();
        }
    },

    _createAndLoadPeriodAppKeyValueStore: function() {
        this.periodappkeyvalue_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.periodappkeyvalue_store.proxy.setDevilryFilters([{
            field: 'period__parentnode__parentnode',
            comp: 'exact',
            value: this.node.get('id')
        }, {
            field: 'period__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'period__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'application',
            comp: 'exact',
            value: 'statistics-qualifiesforexam'
        }, {
            field: 'key',
            comp: 'exact',
            value: 'ready-for-export'
        }]);
        this.periodappkeyvalue_store.pageSize = 100000;
        this.periodappkeyvalue_store.load({
            scope: this,
            callback: this._onPeriodAppKeyValueStoreLoad
        });
    },

    _onPeriodAppKeyValueStoreLoad: function(records, op) {
        if(!op.success) {
            this._handleLoadError(op, 'Failed to load ready-for-export status on active periods.');
        } else {
            this._populateStore();
        }
    },

    _handleLoadError: function(op, title) {
        console.log('Error', op);
        devilry.extjshelpers.RestProxy.showErrorMessagePopup(op, title);
    },

    _populateStore: function() {
        Ext.each(this.periodstore.data.items, function(periodRecord, index) {
            this.store.add({
                'period_id': periodRecord.get('id'),
                'subject_long_name': periodRecord.get('parentnode__long_name'),
                'period_long_name': periodRecord.get('long_name'),
                'qualifies_for_exam_ready_for_export': null
            });
        }, this);

        Ext.each(this.periodappkeyvalue_store.data.items, function(appKeyValueRecord, index) {
            var period_id = appKeyValueRecord.get('period');
            var periodRecord = this.periodstore.getById(period_id);
            var storeRecord = this.store.getById(period_id);
            storeRecord.set('qualifies_for_exam_ready_for_export', appKeyValueRecord.data);
            storeRecord.commit(); // Removed red corner
        }, this);
    },

    //_sendEmailsToVisible: function() {
        //Ext.each(this.store.data.items, function(record, index) {
            //var periodRecord = this.periodstore.getById(record.get('period_id'));
            //console.log(periodRecord);
        //}, this);
    //}
});
