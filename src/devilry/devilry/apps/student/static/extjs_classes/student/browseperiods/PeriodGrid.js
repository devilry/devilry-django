Ext.define('devilry.student.browseperiods.PeriodGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.student-browseperiods-periodgrid',
    
    constructor: function(config) {
        this.createStore();
        this.createRelatedStudentKeyValueStore();
        this.studentkeyvalue_store.load({
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this.labelsGroupedByPeriod = this._groupLabelsByPeriod();
                    this.store.load();
                } else {
                    Ext.MessageBox.alert('Failed to load a resource. Please try to reload the page.');
                }
            },
        });
        this.callParent([config]);
    },

    cellTpl: Ext.create('Ext.XTemplate',
        '<div style="margin-bottom: 3px;">{period.parentnode__short_name}.{period.short_name}</div>',
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
            autoSync: true
        });
        this.store.proxy.setDevilryOrderby(['parentnode__short_name', '-start_time']);
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
            cls: 'selectable-grid',
            columns: [{
                header: 'Subject/course', dataIndex: 'parentnode__short_name', flex: 1,
                renderer: function(value, m, record) {
                    return this.cellTpl.apply({
                        period: record.data,
                        labels: this.labelsGroupedByPeriod[record.get('id')]
                    });
                }
            }]
        });
        this.callParent(arguments);
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
    }
});
