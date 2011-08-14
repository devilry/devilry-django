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
        '    <tpl if="id == current_assignment_group.id">',
        '        &mdash; <strong>(currently selected)</strong>',
        '    </tpl>',
        '</section>'
    ),

    config: {
        /**
         * @cfg
         * AssignmentGroup ``Ext.data.Store``.
         */
        store: undefined,

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
        var me = this;
        Ext.apply(this, {
            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                tdCls: 'selectable-gridcell',
                renderer: function(value, metaData, grouprecord) {
                    //console.log(grouprecord.data);
                    var data = {
                        current_assignment_group: me.assignmentgroup_recordcontainer.record.data
                    };
                    Ext.apply(data, grouprecord.data);
                    return this.rowTpl.apply(data);
                }
            }],
            listeners: {
                scope: this,
                itemmouseup: this.onSelectGroup
            },
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
        }, {
            field: 'is_open',
            comp: 'exact',
            value: true
        }]);
        this.store.load();
    },
});
