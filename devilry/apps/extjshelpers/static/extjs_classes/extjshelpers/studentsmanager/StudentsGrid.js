Ext.define('devilry.extjshelpers.studentsmanager.StudentsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.studentsmanager_studentsgrid',
    cls: 'widget-studentsmanager_studentsgrid',
    sortableColumns: false,

    config: {
        assignmentid: undefined
    },

    mixins: {
        canPerformActionsOnSelected: 'devilry.extjshelpers.GridPeformActionOnSelected'
    },

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

    pointsColTpl: Ext.create('Ext.XTemplate', 
        '<span class="pointscolumn">',
        '    <tpl if="feedback">',
        '       {feedback__points}',
        '    </tpl>',
        '    <tpl if="!feedback">',
        '       <div class="nofeedback">&empty;</div>',
        '   </tpl>',
        '</span>'
    ),

    gradeColTpl: Ext.create('Ext.XTemplate', 
        '<div class="gradecolumn">',
        '   <tpl if="feedback">',
        '        <div class="grade">Grade: {feedback__grade}</div>',
        '        <div class="passing_grade">Passing grade? {feedback__is_passing_grade}</div>',
        '        <div class="grade"></div>',
        '   </tpl>',
        '    <tpl if="!feedback">',
        '        <div class="nofeedback">',
        '           No feedback',
        '        </div>',
        '    </tpl>',
        '</div>'
    ),

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.store.pageSize = 12; // TODO: Default to 30
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode',
            comp: 'exact',
            value: this.assignmentid
        }]);


        this.selModel = Ext.create('Ext.selection.CheckboxModel', {
            checkOnly: true
        });

        Ext.apply(this, {
            dockedItems: [{
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: true
            }],

            columns: [{
                text: 'Group name', dataIndex: 'name', flex: 2
            }, {
                text: 'Students', dataIndex: 'id', flex: 2,
                renderer: this.formatCandidatesCol
            }, {
                text: 'Examiners', dataIndex: 'id', flex: 2,
                renderer: this.formatExaminersCol
            }, {
                text: 'Deliveries', dataIndex: 'number_of_deliveries', flex: 1
            }, {
                text: 'Latest feedback',
                columns: [{
                    text: 'Points',
                    dataIndex: 'feedback__points',
                    renderer: this.formatPointsCol,
                    width: 70
                }, {
                    text: 'Grade',
                    dataIndex: 'feedback__grade',
                    width: 150,
                    renderer: this.formatGradeCol
                }]
            }]
        });
        this.callParent(arguments);
        this.store.load();
    },

    formatCandidatesCol: function(value, p, record) {
        return this.candidatesCol.apply(record.data);
    },

    formatExaminersCol: function(value, p, record) {
        return this.examinersCol.apply(record.data);
    },

    formatPointsCol: function(value, p, record) {
        return this.pointsColTpl.apply(record.data);
    },

    formatGradeCol: function(value, p, record) {
        return this.gradeColTpl.apply(record.data);
    }
});
