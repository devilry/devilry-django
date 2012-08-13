Ext.define('devilry.student.browseperiods.PeriodGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.student-browseperiods-periodgrid',

    requires: [
        'Ext.window.MessageBox',
        'devilry.apps.student.simplified.SimplifiedPeriod',
        'devilry.apps.student.simplified.SimplifiedRelatedStudentKeyValue'
    ],

    
    constructor: function(config) {
        this.createStore();
        this.createRelatedStudentKeyValueStore();
        this.callParent([config]);
    },

    cellTpl: Ext.create('Ext.XTemplate',
        '<div>{period.parentnode__short_name}.{period.short_name}</div>',
        '<ul class="labels-list">',
        '    <tpl for="labels">',
        '       <li class="label-{label}">{label}</li>',
        '    </tpl>',
        '</ul>'
    ),

    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.student.simplified.SimplifiedPeriod',
            remoteFilter: false,
            remoteSort: false,
            autoSync: true,
            groupField: 'long_name',
            remoteGroup: false
        });
        this.store.proxy.setDevilryOrderby(['-start_time']);
        //this.store.proxy.setDevilryOrderby(['parentnode__short_name', '-start_time']);
        this.store.pageSize = 100000;
    },

    createRelatedStudentKeyValueStore: function() {
        this.studentkeyvalue_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.student.simplified.SimplifiedRelatedStudentKeyValue',
            remoteFilter: false,
            remoteSort: false,
            autoSync: true
        });
        this.studentkeyvalue_store.proxy.setDevilryFilters([{
            field: 'application',
            comp: 'exact',
            value: 'devilry.statistics.Labels'
        }]);
        this.studentkeyvalue_store.pageSize = 100000;
    },
    
    initComponent: function() {
        Ext.apply(this, {
            title: gettext('Subject'),
            hideHeaders: true,
            tbar: [{
                xtype: 'textfield',
                emptyText: gettext('Filter') + ' ...',
                flex: 1,
                listeners: {
                    scope: this,
                    change: this._onFilterChange
                }
            }],
            columns: [{
                header: gettext('Subject'),
                dataIndex: 'parentnode__short_name',
                flex: 1,
                sortable: false,
                menuDisabled: true,
                renderer: function(value, m, record) {
                    return this.cellTpl.apply({
                        period: record.data,
                        labels: this.labelsGroupedByPeriod[record.get('id')]
                    });
                }
            }],
            features: [{
                ftype: 'grouping',
                groupHeaderTpl: '{name}'
            }]
        });

        this.on('render', this._onRender, this);
        this.callParent(arguments);
    },

    _onRender: function() {
        this.studentkeyvalue_store.load({
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this.labelsGroupedByPeriod = this._groupLabelsByPeriod();
                    this.store.load({
                        scope: this,
                        callback: function(records, op) {
                            if(op.success) {
                                this._onLoadSuccess();
                            } else {
                                this._showError('Failed to load period store. Please try to reload the page.');
                            }
                        }
                    });
                } else {
                    this._showError('Failed to load key-value resource containing results. Please try to reload the page.');
                }
            }
        });
    },

    _showError: function(message) {
        Ext.MessageBox.alert('Error', message);
    },

    _onLoadSuccess: function() {
        this.fireEvent('allStoresLoadedSuccessfully', this.store, this.studentkeyvalue_store)
    },

    _groupLabelsByPeriod: function() {
        var labelsGroupedByPeriod = {};
        for(labelRecordIndex in this.studentkeyvalue_store.data.items) {
            var labelRecord = this.studentkeyvalue_store.getAt(labelRecordIndex);
            var periodid = labelRecord.get('relatedstudent__period');
            if(!labelsGroupedByPeriod[periodid]) {
                labelsGroupedByPeriod[periodid] = [];
            }
            labelsGroupedByPeriod[periodid].push({label: labelRecord.get('key')});
        }
        return labelsGroupedByPeriod;
    },

    _onFilterChange: function(textfield, newvalue, oldvalue) {
        if(Ext.String.trim(newvalue) == '') {
            this.store.clearFilter();
        } else {
            this._filterByValue(newvalue);
        }
    },


    _filterByValue: function(value) {
        var filterFields = [
            'long_name', 'short_name',
            'parentnode__short_name', 'parentnode__long_name'
        ];
        var filtervalue = value.toLocaleLowerCase();
        this.store.filterBy(function(periodRecord) {
            for(var index=0; index<filterFields.length; index++)  {
                var fieldname = filterFields[index];
                var fieldvalue = periodRecord.get(fieldname);
                if(fieldvalue.indexOf(filtervalue) != -1) {
                    return true;
                }
            }
        }, this);
    }
});
