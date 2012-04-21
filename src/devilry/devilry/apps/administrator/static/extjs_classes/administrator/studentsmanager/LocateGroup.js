Ext.define('devilry.administrator.studentsmanager.LocateGroup', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.locategroup',
    cls: 'widget-locategroup selectable-grid',

    rowTpl: Ext.create('Ext.XTemplate',
        '<div class="section popuplistitem">',
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
        '</div>'
    ),

    requires: [
        'devilry.extjshelpers.formfields.StoreSearchField'
    ],

    deliveriesColTpl: Ext.create('Ext.XTemplate', 
        '<span class="deliveriescol">',
        '    <tpl if="number_of_deliveries &gt; 0">',
        '       {number_of_deliveries}',
        '    </tpl>',
        '    <tpl if="number_of_deliveries == 0">',
        '       <span class="nodeliveries">0</div>',
        '   </tpl>',
        '</span>'
    ),

    config: {
        /**
         * @cfg
         * AssignmentGroup ``Ext.data.Store``. (Required).
         */
        store: undefined,

        groupRecord: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var me = this;

        this.searchfield = Ext.widget('storesearchfield', {
            emptyText: 'Search...',
            store: this.store,
            pageSize: 30,
            width: 300,
            autoLoadStore: true,
            alwaysAppliedFilters: [{
                field: 'is_open',
                comp: 'exact',
                value: false
            }]
        });

        //var searchdefault = '';
        //Ext.each(this.groupRecord.data.candidates__student__username, function(username, index) {
            //searchdefault += username + ' ';
        //});
        //console.log(searchdefault);
        //var searchdefault = ''
        //this.searchfield.setValue(searchdefault);

        Ext.apply(this, {
            columns: [{
                header: 'Students',
                dataIndex: 'id',
                flex: 2,
                renderer: function(value, metaData, grouprecord) {
                    return this.rowTpl.apply(grouprecord.data);
                }
            }, {
                text: 'Group name', dataIndex: 'name', flex: 1
            }, {
                text: 'Deliveries', dataIndex: 'id', width: 70,
                renderer: function(v, p, record) { return this.deliveriesColTpl.apply(record.data); }
            }],

            listeners: {
                scope: this,
                itemmouseup: this.onSelectGroup
            },

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                items: [this.searchfield]
            }, {
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: true
            }]
        });

        this.callParent(arguments);
    },

    onSelectGroup: function(grid, assignmentgroupRecord) {
        console.log('selected');
    },
});
