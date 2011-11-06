Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.ListOfAssignments', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-listofassignments',
    hideHeaders: true,

    recordTpl: Ext.create('Ext.XTemplate',
        '<tpl if="assignmentRecords.length &gt; 1">',
        '    {prefix}',
        '    <tpl for="assignmentRecords">',
        '        {data.short_name}<tpl if="xindex &lt; xcount">{parent.splitter}</tpl>',
        '    </tpl>',
        '</tpl>',
        '<tpl if="assignmentRecords.length == 1">',
        '    <tpl for="assignmentRecords">',
        '        {data.short_name}',
        '    </tpl>',
        '</tpl>'
    ),

    config: {
        rowPrefix: '',
        rowSplitter: ' OR ',
        assignment_store: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.store = Ext.create('Ext.data.ArrayStore', {
            autoDestroy: true,
            idIndex: 0,
            fields: ['assignmentIds']
        });
        this.store.add([{
            assignmentIds: [1, 3]
        }, {
            assignmentIds: [2]
        }])

        Ext.apply(this, {
            columns: [{
                header: 'Assignments', dataIndex: 'assignmentIds', flex: 1,
                renderer: function(assignmentIds, p, record) {
                    return this.recordTpl.apply({
                        assignmentRecords: this._getAssignmentRecordsFromIds(assignmentIds),
                        prefix: this.rowPrefix,
                        splitter: this.rowSplitter
                    });
                }
            }],
            bbar: [{
                xtype: 'button',
                text: 'Add assignment',
                iconCls: 'icon-add-16',
                listeners: {
                    scope: this,
                    click: this._onClickAdd
                }
            }]
        });
        this.callParent(arguments);
    },

    _onClickAdd: function() {
        var me = this;
        Ext.Msg.prompt('Assignment(s)', 'Please enter short name of one or more assignment(s) separated by comma:', function(btn, text){
            if(btn == 'ok'){
                var assignmentShortNames = me._parseAssignmentSpec(text);
                var assignmentIds = me._convertShortnamesToIds(assignmentShortNames);
                me._addToStore(assignmentIds);
            }
        });
    },

    _parseAssignmentSpec: function(assignmentShortNames) {
        return assignmentShortNames.split(/\s*,\s*/);;
    },

    _convertShortnamesToIds: function(assignmentShortNames) {
        var ids = [];
        Ext.each(assignmentShortNames, function(short_name, index) {
            var assignmentRecord = this.assignment_store.findRecord('short_name', short_name);
            if(!assignmentRecord) {
                throw Ext.String.format("Invalid short name: {0}", short_name);
            }
            ids.push(assignmentRecord.get('id'));
        }, this);
        return ids;
    },

    _addToStore: function(assignmentIds) {
        this.store.add({
            assignmentIds: assignmentIds
        });
    },

    _getAssignmentRecordsFromIds: function(assignmentIds) {
        return this.statics().getAssignmentRecordsFromIds(this.assignment_store, assignmentIds);
    },

    getArrayOfAssignmentIds: function() {
        var ids = [];
        Ext.each(this.store.data.items, function(record, index) {
            ids.push(record.get('assignmentIds'));
        }, this);
        return ids;
    },

    statics: {
        getAssignmentRecordsFromIds: function(assignment_store, assignmentIds) {
            var assignmentRecords = [];
            Ext.each(assignmentIds, function(assignmentId, index) {
                var assignmentRecord = assignment_store.findRecord('id', assignmentId);
                assignmentRecords.push(assignmentRecord);
            });
            return assignmentRecords;
        }
    }
});
