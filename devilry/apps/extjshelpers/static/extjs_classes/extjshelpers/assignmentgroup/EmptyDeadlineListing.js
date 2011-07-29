Ext.define('devilry.extjshelpers.assignmentgroup.EmptyDeadlineListing', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.emptydeadlinelisting',
    cls: 'widget-emptydeadlinelisting',
    hideHeaders: true, // Hide column header
    rowTpl: Ext.create('Ext.XTemplate',
        '{deadline:date}'
    ),

    config: {
        /**
         * @cfg
         * Deadline ``Ext.data.Model``.
         */
        deadlinemodel: undefined,

        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for AssignmentGroup.
         */
        assignmentgroup_recordcontainer: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.store = this.createDeadlineStore();
        Ext.apply(this, {
            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                tdCls: 'selectable-gridcell',
                renderer: function(value, metaData, deadlinerecord) {
                    return this.rowTpl.apply(deadlinerecord.data);
                }
            }],
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

    /**
     * @private
     * Reload all empty deadlines on this assignmentgroup.
     * */
    reload: function() {
        this.loadDeadlines(this.assignmentgroup_recordcontainer.record.data.id);
    },

    /**
     * @private
     */
    loadDeadlines: function(assignmentgroupid) {
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'assignment_group',
            comp: 'exact',
            value: assignmentgroupid
        }]);
        this.store.load();
    },

    /**
     * @private
     * */
    createDeadlineStore: function() {
        var deadlinestore = Ext.create('Ext.data.Store', {
            model: this.deadlinemodel,
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        deadlinestore.proxy.extraParams.orderby = Ext.JSON.encode(['-deadline']);
        return deadlinestore;
    },
});
