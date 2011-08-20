Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.assignmentgrouptodolist',
    cls: 'widget-assignmentgrouptodolist',
    hideHeaders: true, // Hide column header
    rowTpl: Ext.create('Ext.XTemplate',
        '<section class="popuplistitem">',
        '    <tpl if="name">',
        '        {name}: ',
        '    </tpl>',
        '    <ul style="display: inline-block;">',
        '    <tpl for="candidates__identifier">',
        '        <li>{.}</li>',
        '    </tpl>',
        '    </ul>',
        '    <tpl if="id == current_assignment_group_id">',
        '        &mdash; <strong>(currently selected)</strong>',
        '    </tpl>',
        '</section>'
    ),

    requires: [
        'devilry.extjshelpers.formfields.StoreSearchField'
    ],

    config: {
        /**
         * @cfg
         * AssignmentGroup ``Ext.data.Store``. (Required).
         */
        store: undefined,

        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for AssignmentGroup. (Optional).
         *
         * Used to show current assignmentgroup.
         */
        assignmentgroup_recordcontainer: undefined,

        pageSize: 10,
        tbarExtra: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var me = this;

        this.tbarItems = [{
            xtype: 'storesearchfield',
            emptyText: 'Search...',
            store: this.store,
            width: 300,
            autoLoad: false
        }];
        if(this.tbarExtra) {
            Ext.Array.insert(this.tbarItems, 1, this.tbarExtra);
        }

        Ext.apply(this, {
            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                tdCls: 'selectable-gridcell',
                renderer: function(value, metaData, grouprecord) {
                    //console.log(grouprecord.data);
                    var data = {};
                    if(me.assignmentgroup_recordcontainer) {
                        data.current_assignment_group_id = me.assignmentgroup_recordcontainer.record.data.id;
                    }
                    Ext.apply(data, grouprecord.data);
                    return this.rowTpl.apply(data);
                }
            }],
            listeners: {
                scope: this,
                itemmouseup: this.onSelectGroup
            },


            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                items: this.tbarItems
            }, {
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: true
            }]
        });

        this.callParent(arguments);

        if(this.assignmentgroup_recordcontainer) {
            if(this.assignmentgroup_recordcontainer.record) {
                this.onSetAssignmentGroup();
            }
            this.assignmentgroup_recordcontainer.addListener('setRecord', this.onSetAssignmentGroup, this);
        }
    },

    onSelectGroup: function(grid, assignmentgroupRecord) {
        window.location.href = assignmentgroupRecord.data.id.toString();
    },

    /**
     * @private
     */
    onSetAssignmentGroup: function() {
        this.loadTodoListForAssignment(this.assignmentgroup_recordcontainer.record.data.parentnode);
    },

    /**
     * Reload store with the given assignmentid.
     * */
    loadTodoListForAssignment: function(assignmentid) {
        this.store.pageSize = this.pageSize;
        var searchfield = this.down('storesearchfield');
        searchfield.alwaysAppliedFilters = [{
            field: 'parentnode',
            comp: 'exact',
            value: assignmentid
        }, {
            field: 'is_open',
            comp: 'exact',
            value: true
        }];
        searchfield.refreshStore();
    },
});
