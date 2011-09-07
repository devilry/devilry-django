Ext.define('devilry.extjshelpers.studentsmanager.StudentsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.studentsmanager_studentsgrid',
    cls: 'widget-studentsmanager_studentsgrid',
    sortableColumns: true,

    config: {
        assignmentid: undefined,
        dockedItems: []
    },

    mixins: {
        canPerformActionsOnSelected: 'devilry.extjshelpers.GridPeformActionOnSelected'
    },

    infoColTpl: Ext.create('Ext.XTemplate', 
        '<section class="infocolumn">',
        '    <div>',
        '        <tpl if="is_open">',
        '           <span class="group_is_open">Open</span>',
        '        </tpl>',
        '        <tpl if="!is_open">',
        '           <span class="group_is_closed">Closed</span>',
        '       </tpl>',
        '    </div>',
        '    <div>',
        '        <tpl if="latest_deadline_id === null">',
        '           <span class="has_no_deadlines">No deadlines</span>',
        '        </tpl>',
        '    </div>',
        '</section>'
    ),

    candidatesCol: Ext.create('Ext.XTemplate', 
        '<ul class="candidatescolumn">',
        '    <tpl for="candidates__identifier">',
        '       <li>{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    examinersCol: Ext.create('Ext.XTemplate', 
        '<ul class="examinerscolumn">',
        '    <tpl for="examiners__username">',
        '       <li>{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

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

    pointsColTpl: Ext.create('Ext.XTemplate', 
        '<span class="pointscolumn">',
        '    <tpl if="feedback">',
        '       {feedback__points}',
        '    </tpl>',
        '    <tpl if="!feedback">',
        '       <span class="nofeedback">&empty;</span>',
        '   </tpl>',
        '</span>'
    ),

    gradeColTpl: Ext.create('Ext.XTemplate', 
        '<section class="gradecolumn">',
        '   <tpl if="feedback">',
        '        <div class="is_passing_grade">',
        '           <tpl if="feedback__is_passing_grade"><span class="passing_grade">Passed</span></tpl>',
        '           <tpl if="!feedback__is_passing_grade"><span class="not_passing_grade">Failed</span></tpl>',
        '           : <span class="grade">{feedback__grade}</span>',
        '        </div>',
        '        <div class="delivery_type">',
        '            <tpl if="feedback__delivery__delivery_type == 0"><span class="electronic">Electronic</span></tpl>',
        '            <tpl if="feedback__delivery__delivery_type == 1"><span class="non-electronic">Non-electronic</span></tpl>',
        '            <tpl if="feedback__delivery__delivery_type == 2"><span class="alias">From previous period</span></tpl>',
        '            <tpl if="feedback__delivery__delivery_type &gt; 2"><span class="unknown">Unknown delivery type</span></tpl>',
        '       </div>',
        '   </tpl>',
        '    <tpl if="!feedback">',
        '        <div class="nofeedback">',
        '           No feedback',
        '        </div>',
        '    </tpl>',
        '</section>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.store.pageSize = 30;
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode',
            comp: 'exact',
            value: this.assignmentid
        }]);


        this.selModel = Ext.create('Ext.selection.CheckboxModel', {
            checkOnly: true
        });

        Ext.apply(this, {
            //listeners: {
                //scope: this,
                //itemclick: function(grid, record) {
                    //if(grid.getSelectionModel().isSelected(record)) {
                        //grid.getSelectionModel().deselect(record);
                    //} else {
                        //grid.getSelectionModel().select(record, true);
                    //}
                //}
            //},

            columns: [{
                text: '', dataIndex: 'is_open', width: 100,
                menuDisabled: true,
                renderer: this.formatInfoCol
            }, {
                text: 'Students', dataIndex: 'id', flex: 4,
                menuDisabled: true,
                renderer: this.formatCandidatesCol
            }, {
                text: 'Deliveries', dataIndex: 'number_of_deliveries', flex: 2,
                menuDisabled: true,
                renderer: this.formatDeliveriesCol
            }, {
                text: 'Latest feedback',
                menuDisabled: true,
                columns: [{
                    text: 'Points',
                    dataIndex: 'feedback__points',
                    renderer: this.formatPointsCol,
                    menuDisabled: true,
                    width: 70
                }, {
                    text: 'Grade',
                    dataIndex: 'feedback__grade',
                    width: 150,
                    menuDisabled: true,
                    renderer: this.formatGradeCol
                }]
            }, {
                text: 'Examiners', dataIndex: 'id', flex: 4,
                menuDisabled: true,
                renderer: this.formatExaminersCol
            }, {
                text: 'Group name', dataIndex: 'name', flex: 3,
                menuDisabled: true
            }]
        });

        this.dockedItems.push({
            xtype: 'pagingtoolbar',
            store: this.store,
            dock: 'bottom',
            displayInfo: true
        });

        this.callParent(arguments);
        this.store.load();
    },

    formatInfoCol: function(value, p, record) {
        return this.infoColTpl.apply(record.data);
    },

    formatCandidatesCol: function(value, p, record) {
        return this.candidatesCol.apply(record.data);
    },

    formatExaminersCol: function(value, p, record) {
        return this.examinersCol.apply(record.data);
    },

    formatDeliveriesCol: function(value, p, record) {
        return this.deliveriesColTpl.apply(record.data);
    },

    formatPointsCol: function(value, p, record) {
        return this.pointsColTpl.apply(record.data);
    },

    formatGradeCol: function(value, p, record) {
        return this.gradeColTpl.apply(record.data);
    }
});
