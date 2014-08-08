Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.assignmentgrouptodolist',
    cls: 'widget-assignmentgrouptodolist',
    requires: [
        'devilry.extjshelpers.formfields.StoreSearchField'
    ],

    studentsColTpl: Ext.create('Ext.XTemplate',
        '<div class="section popuplistitem">',
            '<a href="{groupUrlPrefix}{id}" style="display: block;">',
            '<tpl if="name">',
                '{name}: ',
            '</tpl>',
            '<tpl for="candidates">',
                '{identifier} <tpl if="full_name">({full_name})</tpl>',
                '<tpl if="xindex < xcount">, </tpl>',
            '</tpl>',
            '<tpl if="id == current_assignment_group_id">',
                ' &mdash; <strong>(', gettext('currently selected'), ')</strong>',
            '</tpl>',
            '</a>',
        '</div>'
    ),

    deliveriesColTpl: Ext.create('Ext.XTemplate', 
        '<div class="section popuplistitem">',
        '<span class="deliveriescol">',
        '    <tpl if="number_of_deliveries &gt; 0">',
        '       {number_of_deliveries}',
        '    </tpl>',
        '    <tpl if="number_of_deliveries == 0">',
        '       <span class="nodeliveries">0</div>',
        '   </tpl>',
        '</span>',
        '</div>'
    ),

    todohelptext: [
        '<p>',
            interpolate(gettext('This is your to-do list on this %(assignment_term)s. It shows all <em>open</em> %(groups_term)s. An <em>open</em> %(group_term)s is a %(group_term)s that is still waiting for %(deliveries_term)s or %(feedback_term)s.'), {
                assignment_term: gettext('assignment'),
                groups_term: gettext('groups'),
                group_term: gettext('group'),
                deliveries_term: gettext('deliveries'),
                feedback_term: gettext('feedback')
            }, true),
        '</p>'
    ].join(''),

    /**
     * @cfg
     * The name of the assignment group ``Ext.data.Model`` to use in the store
     * (Required).  The store copies the proxy from this model.
     *
     */
    assignmentgroupmodelname: undefined,

    /**
    * @cfg
    * A {@link devilry.extjshelpers.SingleRecordContainer} for AssignmentGroup. (Optional).
    *
    * This is optional, however if it is not provided, you will have to call
    * loadTodoListForAssignment(assignmentid) manually to load data into the
    * store.
    */
    assignmentgroup_recordcontainer: undefined,

    /**
     * @cfg
     */
    pageSize: 7,

    /**
     * @cfg
     * (Optional)
     */
    toolbarExtra: undefined,

    /**
     * @cfg
     * (Optional)
     */
    helpTpl: Ext.create('Ext.XTemplate',
        '<div class="section helpsection">{todohelptext}</div>'
    ),

    initComponent: function() {
        this._createStore();
        var me = this;
        this.tbarItems = [{
            xtype: 'storesearchfield',
            emptyText: gettext('Search') + ' ...',
            store: this.store,
            pageSize: this.pageSize,
            width: 300,
            autoLoadStore: false
        }];
        if(this.toolbarExtra) {
            Ext.Array.insert(this.tbarItems, 1, this.toolbarExtra);
        }

        var groupUrlPrefix = this.getGroupUrlPrefix();
        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                flex: 6,
                xtype: 'grid',
                disableSelection: true,
                //rowLines: false,
                store: this.store,
                frame: false,
                border: false,
                sortableColumns: false,
                autoScroll: true,
                columns: [{
                    header: gettext('Students'),
                    dataIndex: 'id',
                    flex: 2,
                    menuDisabled: true,
                    renderer: function(value, metaData, grouprecord) {
                        var data = {
                            groupUrlPrefix: groupUrlPrefix
                        };
                        if(me.assignmentgroup_recordcontainer) {
                            data.current_assignment_group_id = me.assignmentgroup_recordcontainer.record.data.id;
                        }
                        Ext.apply(data, grouprecord.data);
                        return me.studentsColTpl.apply(data);
                    }
                }, {
                    text: gettext('Deliveries'), dataIndex: 'id', width: 100, menuDisabled: true,
                    renderer: function(v, p, record) { return me.deliveriesColTpl.apply(record.data); }
                }],

                listeners: {
                    scope: this,
                    render: this._onRenderGrid
                }
            }, {
                xtype: 'box',
                width: 300,
                autoScroll: true,
                flex: 4,
                html: this.helpTpl.apply({todohelptext: this.todohelptext})
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                //ui: 'footer',
                items: this.tbarItems
            }, {
                xtype: 'pagingtoolbar',
                store: me.store,
                dock: 'bottom',
                displayInfo: true
            }]
        });

        this.callParent(arguments);

    },

    _onRenderGrid: function() {
        Ext.defer(function() {
            if(this.assignmentgroup_recordcontainer) {
                if(this.assignmentgroup_recordcontainer.record) {
                    this.onSetAssignmentGroup();
                }
                this.assignmentgroup_recordcontainer.addListener('setRecord', this.onSetAssignmentGroup, this);
            }
            this.down('searchfield').focus();
        }, 300, this);
    },

    _createStore: function() {
        var model = Ext.ModelManager.getModel(this.assignmentgroupmodelname);
        this.store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
        });
    },

    getGroupUrlPrefix: function() {
        return '';
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
