Ext.define('devilry.extjshelpers.assignmentgroup.DeadlinesOnSingleGroupListing', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deadlinesonsinglegrouplisting',
    cls: 'widget-deadlinesonsinglegrouplisting',
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
        assignmentgroup_recordcontainer: undefined,

        /**
         * @cfg
         * Enable creation of new deadlines?
         */
        enableDeadlineCreation: false,
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        if(this.enableDeadlineCreation) {
            this.addCreateNewDeadlineButton();
        }
        this.store = this.createDeadlineStore();
        Ext.apply(this, {
            columns: [{
                header: 'Deadline',
                dataIndex: 'deadline',
                flex: 1,
                renderer: function(value, metaData, deadlinerecord) {
                    return this.rowTpl.apply(deadlinerecord.data);
                }
            }, {
                header: 'Text',
                dataIndex: 'text',
                flex: 2
            }, {
                header: 'Deliveries',
                dataIndex: 'number_of_deliveries',
                flex: 1
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
        Ext.apply(this, {
            tbar: ['->', {
                xtype: 'button',
                text: 'Create new deadline',
                iconCls: 'icon-add-32',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this.onCreateNewDeadline
                }
            }]
        });
    },

    /**
     * @private
     */
    onCreateNewDeadline: function() {
        var deadlineRecord = Ext.create(this.deadlinemodel, {
            'assignment_group': this.assignmentgroup_recordcontainer.record.data.id
        });

        var me = this;
        var createDeadlineWindow = Ext.create('devilry.extjshelpers.RestfulSimplifiedEditWindowBase', {
            title: 'Create deadline',
            width: 500,
            height: 300,
            editpanel: Ext.ComponentManager.create({
                xtype: 'restfulsimplified_editpanel',
                modelname: this.deadlinemodel,
                //editformitems: assignmentgroupoverview_deadline_editformitems,
                editform: Ext.create('devilry.extjshelpers.forms.Deadline'),
                //foreignkeyfieldnames: assignmentgroupoverview_deadline_foreignkeyfieldnames,
                record: deadlineRecord
            }),
            onSaveSuccess: function(record) {
                this.close();
                me.reload();
            }
        });
        createDeadlineWindow.show();
    }
});
