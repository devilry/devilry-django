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



    /**
     * Call the given action on each selected item. If all items on the current page is selected,
     * a MessageBox will be shown to the user where they can choose to call the action on all items
     * instead of just the ones on the current page.
     *
     * @param action See {@link #performActionOnAll}.
     */
    performActionOnSelected: function(action) {
        var selected = this.selModel.getSelection();
        var totalOnCurrentPage = this.store.getCount();
        if(selected.length === totalOnCurrentPage) {
            // TODO: Ask if _all_
            this.performActionOnAll(action);
        } else {
            this._performActionOnSelected(action, selected, 1, selected.length);
        }
    },


    /**
     * Call the given action on each item in the store (on all pages in the store).
     *
     * @param action An object with the following attributes:
     *
     *      callback
     *          A callback function that is called for each record in the
     *          store. The callback gets the folling arguments: `(record,
     *          index, total)`. Index is the index of the record starting with
     *          1, and total is the total number of records.
     *      scope
     *          The scope to execute `callback` in.
     *          
     */
    performActionOnAll: function(action) {
        this._performActionOnAllTmp = {
            originalCurrentPage: this.store.currentPage,
            action: action,
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
            this.store.currentPage = this._performActionOnAllTmp.originalCurrentPage;
            this.store.load();
        } else {
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
        var startIndex = ((pagenum-1) * this.store.pageSize) + 1;
        this._performActionOnSelected(
            this._performActionOnAllTmp.action, records,
            startIndex, this.store.getTotalCount()
        );
        pagenum ++;
        this._performActionOnPage(pagenum);
    },

    /**
     * @private
     */
    _performActionOnSelected: function(action, selected, startIndex, total) {
        Ext.each(selected, function(record, index) {
            Ext.bind(action.callback, action.scope)(record, startIndex + index, total);
        });
    }
});
