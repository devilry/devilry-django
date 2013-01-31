Ext.define('devilry.extjshelpers.assignmentgroup.DeadlinesOnSingleGroupListing', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deadlinesonsinglegrouplisting',
    cls: 'widget-deadlinesonsinglegrouplisting selectable-grid',
    sortableColumns: false,
    requires: [
        'devilry.extjshelpers.assignmentgroup.CreateNewDeadlineWindow'
    ],

    rowTpl: Ext.create('Ext.XTemplate',
        '{deadline:date}'
    ),

    deadlinemodel: undefined,
    assignmentgroup_recordcontainer: undefined,
    enableDeadlineCreation: false,


    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.store = this.createDeadlineStore();
        Ext.apply(this, {
            columns: [{
                header: 'Deadline',
                dataIndex: 'deadline',
                menuDisabled: true,
                width: 150,
                renderer: function(value, metaData, deadlinerecord) {
                    return this.rowTpl.apply(deadlinerecord.data);
                }
            }, {
                header: 'Text',
                dataIndex: 'text',
                menuDisabled: true,
                flex: 2
            }, {
                header: 'Deliveries',
                menuDisabled: true,
                dataIndex: 'number_of_deliveries',
                width: 85
            }]
        });

        this.dockedItems = [{
            xtype: 'pagingtoolbar',
            store: this.store,
            dock: 'bottom',
            displayInfo: false
        }];
        if(this.enableDeadlineCreation) {
            this.addCreateNewDeadlineButton();
        }

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


    /**
     * @private
     * */
    addCreateNewDeadlineButton: function() {
        Ext.Array.insert(this.dockedItems, 0, [{
            xtype: 'toolbar',
            ui: 'footer',
            dock: 'bottom',
            items: ['->', {
                xtype: 'button',
                text: 'Create deadline',
                iconCls: 'icon-add-32',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this.onCreateNewDeadline
                }
            }]
        }]);
    },

    /**
     * @private
     */
    onCreateNewDeadline: function() {
        var me = this;
        var createDeadlineWindow = Ext.widget('createnewdeadlinewindow', {
            assignmentgroupid: this.assignmentgroup_recordcontainer.record.data.id,
            deadlinemodel: this.deadlinemodel,
            onSaveSuccess: function(record) {
                this.close();
                me.reload();
            }
        });
        createDeadlineWindow.show();
    }
});
