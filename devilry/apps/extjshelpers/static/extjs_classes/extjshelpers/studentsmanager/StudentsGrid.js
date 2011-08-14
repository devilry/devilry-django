Ext.define('devilry.extjshelpers.studentsmanager.StudentsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.studentsmanager_studentsgrid',
    cls: 'widget-studentsmanager_studentsgrid',
    sortableColumns: false,

    config: {
        assignmentid: undefined
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
    },


    performActionOnSelected: function(action, loadMaskElement) {
        var selected = this.selModel.getSelection();
        var totalOnCurrentPage = this.store.getCount();
        if(selected.length === totalOnCurrentPage) {
            // TODO: Ask if _all_
            this.performActionOnAll(action, loadMaskElement);
        } else {
            this._performActionOnSelected(action, selected);
        }
    },


    performActionOnAll: function(action, loadMaskElement) {
        this._performActionOnAllTmp = {
            currentPage: this.store.currentPage,
            action: action,
            loadMaskElement: loadMaskElement,
            allRecords: []
        }
        this._performActionOnPage(1);
    },

    /**
     * @private
     */
    _performActionOnPage: function(pagenum) {
        var totalPages = this.store.getTotalCount() / this.store.pageSize;
        if(this.store.getTotalCount() % this.store.pageSize != 0) {
            totalPages = Math.ceil(totalPages);
        }

        if(pagenum > totalPages) {
            this._performActionOnAllTmp.loadMaskElement.unmask();
            this._performActionOnSelected(this._performActionOnAllTmp.action, this._performActionOnAllTmp.allRecords);
        } else {
            tpl = 'Finding all items in table. Processing page {0}/{1}';
            this._performActionOnAllTmp.loadMaskElement.mask(Ext.String.format(tpl, pagenum, totalPages));

            this.store.currentPage = pagenum;
            this.store.load({
                scope: this,
                callback: function(records, op, success) {
                    if(success) {
                        this._performActionOnAllPageLoaded(pagenum, records);
                    } else {
                        throw "Failed to load page";
                    }
                }
            });
        }
    },

    /**
     * @private
     */
    _performActionOnAllPageLoaded: function(pagenum, records) {
        Ext.each(records, function(record, index) {
            this._performActionOnAllTmp.allRecords.push(record);
        }, this);
        pagenum ++;
        this._performActionOnPage(pagenum);
    },

    /**
     * @private
     */
    _performActionOnSelected: function(action, selected) {
        Ext.bind(action.callback, action.scope)(selected);
    }
});
