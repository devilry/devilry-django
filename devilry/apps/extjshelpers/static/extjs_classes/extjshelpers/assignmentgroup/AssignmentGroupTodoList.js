Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.assignmentgrouptodolist',
    cls: 'widget-assignmentgrouptodolist',
    hideHeaders: true, // Hide column header
    rowTpl: Ext.create('Ext.XTemplate',
        '{id}'
    ),

    config: {
        /**
         * @cfg
         * AssignmentGroup ``Ext.data.Model``.
         */
        assignmentgroupmodel: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                tdCls: 'selectable-gridcell',
                renderer: function(value, metaData, grouprecord) {
                    //console.log(grouprecord.data);
                    return this.rowTpl.apply(grouprecord.data);
                }
            }],
            listeners: {
                scope: this,
                itemmouseup: this.onSelectGroup
            },
            dockedItems: [{
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'top',
                displayInfo: false
            }]
        });

        this.callParent(arguments);
        if(this.assignmentgroup_recordcontainer.record) {
            this.reload();
        }
        this.assignmentgroup_recordcontainer.addListener('setRecord', this.reload, this);
    },

    onSelectGroup: function(grid, assignmentgroupRecord) {
        window.location.href = assignmentgroupRecord.data.id.toString();
    },

    /**
     * @private
     * */
    reload: function(assignmentgroupid) {
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode',
            comp: 'exact',
            value: this.assignmentgroup_recordcontainer.record.data.parentnode
        }]);
        this.store.load();
    },

    /**
     * @private
     * */
});
