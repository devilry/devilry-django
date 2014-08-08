Ext.define('devilry.extjshelpers.studentsmanager.StudentsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.studentsmanager_studentsgrid',
    cls: 'widget-studentsmanager_studentsgrid',
    sortableColumns: true,

    requires: [
        'devilry.extjshelpers.GridSelectionModel'
    ],

    config: {
        assignmentid: undefined,
        dockedItems: [],
        isAdministrator: undefined,
        isAnonymous: undefined,
        assignmentrecord: undefined
    },

    mixins: {
        canPerformActionsOnSelected: 'devilry.extjshelpers.GridPeformActionOnSelected'
    },

    infoColTpl: Ext.create('Ext.XTemplate', 
        '<div class="section infocolumn">',
            '<div>',
                '<tpl if="is_open">',
                    '<span class="group_is_open">', gettext('Open'), '</span>',
                '</tpl>',
                '<tpl if="!is_open">',
                    '<span class="group_is_closed">', gettext('Closed'), '</span>',
                '</tpl>',
            '</div>',
            '<div>',
                '<tpl if="latest_deadline_id === null">',
                    '<span class="has_no_deadlines">',
                        interpolate(gettext('No %(deadlines_term)s'), {
                            deadlines_term: gettext('deadlines')
                        }, true),
                    '</span>',
                '</tpl>',
            '</div>',
        '</div>'
    ),

    candidatesCol_old: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="candidates__identifier">',
        '       <li>',
        '           {.}',
        '       </li>',
        '    </tpl>',
        '</ul>'
    ),
    candidatesCol: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="candidates">',
        '       <li>',
        '           <a href="../assignmentgroup/{parent.id}">{identifier}</a>',
        '       </li>',
        '    </tpl>',
        '</ul>'
    ),
    candFullNamesCol: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="candidates">',
        '       <li>',
        '           {full_name}',
        '       </li>',
        '    </tpl>',
        '</ul>'
    ),

    realUsernamesCol: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="candidates__student__username">',
        '       <li><a href="../assignmentgroup/{parent.id}">{.}</a></li>',
        '    </tpl>',
        '</ul>'
    ),

    realFullnamesCol: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="candidates__student__devilryuserprofile__full_name">',
        '       <li>{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    examinersCol: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="examiners__user__username">',
        '       <li>{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    tagsColTpl: Ext.create('Ext.XTemplate', 
        '<ul class="tagscolumn">',
        '    <tpl for="tags__tag">',
        '       <li>{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    activeDeadlineColTpl: Ext.create('Ext.XTemplate', 
        '<span class="activedeadlinecol">{latest_deadline_deadline}</span>'
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
        '<div class="section gradecolumn">',
            '<tpl if="feedback">',
                '<div class="is_passing_grade">',
                    '<tpl if="feedback__is_passing_grade"><span class="passing_grade">', gettext('Passed'), '</span></tpl>',
                    '<tpl if="!feedback__is_passing_grade"><span class="not_passing_grade">', gettext('Failed'), '</span></tpl>',
                    ' : <span class="grade">{feedback__grade}</span>',
                '</div>',
                '<div class="delivery_type">',
                    '<tpl if="feedback__delivery__delivery_type == 0"><span class="electronic">',
                        gettext('Electronic'),
                    '</span></tpl>',
                    '<tpl if="feedback__delivery__delivery_type == 1"><span class="non-electronic">',
                        gettext('Non-electronic'),
                    '</span></tpl>',
                    '<tpl if="feedback__delivery__delivery_type == 2"><span class="alias">',
                        interpolate(gettext('From previous %(period_term)s'), {
                            period_term: gettext('period')
                        }, true),
                    '</span></tpl>',
                    '<tpl if="feedback__delivery__delivery_type &gt; 2"><span class="unknown">',
                        interpolate(gettext('Unknown %(delivery_term)s type'), {
                            delivery_term: gettext('delivery')
                        }, true),
                    '</span></tpl>',
                '</div>',
            '</tpl>',
            '<tpl if="!feedback">',
                '<div class="nofeedback">',
                    'No feedback',
                '</div>',
            '</tpl>',
        '</div>'
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


        this.selModel = Ext.create('devilry.extjshelpers.GridSelectionModel', {
            checkOnly: false
        });

        var studentsCol;
        if(this.isAdministrator) {
            studentsCol = {
                text: gettext('Students'), dataIndex: 'id',
                menuDisabled: true, sortable: false,
                columns: [{
                    text: gettext('Usernames'), dataIndex: 'candidates__student__username', width: 90,
                    menuDisabled: true, sortable: true,
                    renderer: this.formatRealUsernamesCol
                }, {
                    text: gettext('Full names'), dataIndex: 'candidates__student__devilryuserprofile__full_name', width: 155,
                    menuDisabled: true, sortable: true,
                    renderer: this.formatRealFullnamesCol
                }]
            };
            if(this.isAnonymous) {
                studentsCol.columns.push({
                    text: gettext('Candidate ID'), dataIndex: 'candidates__identifier',
                    width: 90,
                    menuDisabled: true, sortable: true,
                    renderer: this.formatCandidatesCol_old
                });
            }
        } else {
            if(this.isAnonymous) {
                studentsCol = {
                    text: gettext('Students'), dataIndex: 'candidates__identifier', flex: 4,
                    menuDisabled: true,
                    sortable: true,
                    renderer: this.formatCandidatesCol
                };
            } else {
                studentsCol = {
                    text: gettext('Students'), dataIndex: 'id',
                    menuDisabled: true, sortable: false,
                    columns: [{
                        text: gettext('Usernames'), dataIndex: 'candidates__identifier',
                        width: 90,
                        menuDisabled: true, sortable: true,
                        renderer: this.formatCandidatesCol
                    }, {
                        text: gettext('Full names'), dataIndex: 'candidates__full_name',
                        width: 155,
                        menuDisabled: true, sortable: true,
                        renderer: this.formatCandFullNamesCol
                    }]
                };
            }
        }

        Ext.apply(this, {
            columns: [{
                text: '', dataIndex: 'is_open', width: 100,
                menuDisabled: true,
                renderer: this.formatInfoCol
            }, studentsCol, {
                text: interpolate(gettext('Latest %(feedback_term)s'), {
                    feedback_term: gettext('feedback')
                }, true),
                menuDisabled: true,
                sortable: false,
                columns: [{
                    text: gettext('Points'),
                    dataIndex: 'feedback__points',
                    renderer: this.formatPointsCol,
                    menuDisabled: true,
                    sortable: true,
                    width: 70
                }, {
                    text: gettext('Grade'),
                    dataIndex: 'feedback__grade',
                    width: 150,
                    menuDisabled: true,
                    sortable: true,
                    renderer: this.formatGradeCol
                }]
            }, {
                text: gettext('Tags'), dataIndex: 'tags__tag', flex: 2,
                menuDisabled: true,
                renderer: this.formatTagsCol
            }, {
                text: gettext('Group name'), dataIndex: 'name', flex: 3,
                menuDisabled: true
            }]
        });
        if(this.isAdministrator) {
            Ext.Array.insert(this.columns, 3, [{
                text: gettext('Examiners'), dataIndex: 'examiners__user__username', flex: 3,
                menuDisabled: true,
                renderer: this.formatExaminersCol
            }]);
        }
        if(this.assignmentrecord.get('delivery_types') != 1) {
            this.columns.push({
                text: interpolate(gettext('Active %(deadline_term)s'), {
                    deadline_term: gettext('deadline')
                }, true),
                dataIndex: 'latest_deadline_deadline', width: 125,
                menuDisabled: true,
                renderer: this.formatActiveDeadlineCol
            });

            Ext.Array.insert(this.columns, 2, [{
                text: gettext('Deliveries'), dataIndex: 'number_of_deliveries', flex: 2,
                menuDisabled: true,
                renderer: this.formatDeliveriesCol
            }]);
        }

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
    formatCandidatesCol_old: function(value, p, record) {
        return this.candidatesCol_old.apply(record.data);
    },
    formatCandFullNamesCol: function(value, p, record) {
        return this.candFullNamesCol.apply(record.data);
    },

    formatRealUsernamesCol: function(value, p, record) {
        return this.realUsernamesCol.apply(record.data);
    },
    formatRealFullnamesCol: function(value, p, record) {
        return this.realFullnamesCol.apply(record.data);
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
    },

    formatActiveDeadlineCol: function(value, p, record) {
        return this.activeDeadlineColTpl.apply(record.data);
    },

    formatTagsCol: function(value, p, record) {
        return this.tagsColTpl.apply(record.data);
    }
});
