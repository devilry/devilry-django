Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.ListOfAssignments', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-listofassignments',
    hideHeaders: true,

    requires: [
        'devilry.statistics.ChooseAssignmentsGrid'
    ],

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
        assignment_store: undefined,
        selected_assignments: undefined
    },

    constructor: function(config) {
        this.store = Ext.create('Ext.data.ArrayStore', {
            autoDestroy: true,
            idIndex: 0,
            fields: ['assignmentIds']
        });

        this.callParent([config]);
        this.initConfig(config);
        if(this.selected_assignments) {
            Ext.each(this.selected_assignments, function(assignmentIds, index) {
                this.store.add({
                    assignmentIds: assignmentIds
                });
            }, this);
        }
    },

    initComponent: function() {
        //this.store.add([{
            //assignmentIds: [1, 3]
        //}, {
            //assignmentIds: [2]
        //}])

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
            tbar: [this.removeButton = Ext.widget('button', {
                text: 'Remove',
                iconCls: 'icon-delete-16',
                disabled: true,
                listeners: {
                    scope: this,
                    click: this._onClickDelete
                }
            }), {
                xtype: 'button',
                text: 'Add',
                iconCls: 'icon-add-16',
                listeners: {
                    scope: this,
                    click: this._onClickAdd
                }
            }]
        });
        this.on('selectionchange', this._onSelectionChange, this);
        this.callParent(arguments);
    },

    _onSelectionChange: function(grid, selected) {
        if(selected.length === 0) {
            this.removeButton.disable();
        } else {
            this.removeButton.enable();
        }
    },

    _onClickDelete: function() {
        var selected = this.getSelectionModel().getSelection();
        if(selected.length != 1) {
            Ext.MessageBox.alert('Error', 'Please select a row from the list.');
            return;
        }
        var selectedItem = selected[0];
        this.store.remove(selectedItem);
    },

    _onClickAdd: function() {
        var me = this;
        Ext.widget('window', {
            layout: 'fit',
            title: 'Select one or more assignment(s)',
            width: 500,
            height: 350,
            modal: true,
            items: {
                xtype: 'statistics-chooseassignmentsgrid',
                hideHeaders: true,
                store: this.assignment_store
            },
            bbar: ['->', {
                xtype: 'button',
                text: 'Add assignment(s)',
                scale: 'large',
                iconCls: 'icon-add-32',
                listeners: {
                    scope: this,
                    click: this._onAdd
                }
            }]
        }).show();
    },

    _onAdd: function(button) {
        var win = button.up('window');
        var grid = win.down('statistics-chooseassignmentsgrid');
        if(grid.checkAtLeastOneSelected()) {
            win.close();
            var assignmentIds = grid.getIdOfSelected();
            this._addToStore(assignmentIds);
        }
    },

    _parseAssignmentSpec: function(assignmentShortNames) {
        return assignmentShortNames.split(/\s*,\s*/);
    },

    _addToStore: function(assignmentIds) {
        this.store.add({
            assignmentIds: assignmentIds
        });
    },

    _getAssignmentRecordsFromIds: function(assignmentIds) {
        var assignmentRecords = [];
        Ext.each(assignmentIds, function(assignmentId, index) {
            var assignmentRecordIndex = this.assignment_store.findExact('id', assignmentId);
            var assignmentRecord = this.assignment_store.getAt(assignmentRecordIndex);
            assignmentRecords.push(assignmentRecord);
        }, this);
        return assignmentRecords;
    },

    getArrayOfAssignmentIds: function() {
        var ids = [];
        Ext.each(this.store.data.items, function(record, index) {
            ids.push(record.get('assignmentIds'));
        }, this);
        return ids;
    }
});
