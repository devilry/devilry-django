Ext.define('devilry.extjshelpers.assignmentgroup.DeadlinesOnSingleGroupListing', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deadlinesonsinglegrouplisting',
    cls: 'widget-deadlinesonsinglegrouplisting',
    hideHeaders: true, // Hide column header
    rowTpl: Ext.create('Ext.XTemplate',
        '{deadline:date} ({number_of_deliveries} deliveries)'
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
                dock: 'bottom',
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
        this.store.load({
            scope: this,
            callback: this.onDeadlineStoreLoad
        });
    },

    /**
     * @private
     */
    onDeadlineStoreLoad: function(records, op, success) {
        this.setTitle(Ext.String.format(
            '{0} ({1})',
            this.title,
            this.store.getTotalCount()
        ));
        if(this.store.getTotalCount() == 0) {
            this.disable();
        }
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
