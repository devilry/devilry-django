Ext.define('devilry.statistics.dataview.FullGridView', {
    extend: 'devilry.statistics.dataview.MinimalGridView',
    cellTpl: Ext.create('Ext.XTemplate',
        '<tpl if="has_feedback">',
        '   <tpl if="is_open">',
        '       <span class="nofeedback">Not finished</span>',
        '   </tpl>',
        '   <tpl if="!is_open">',
        '      {scaled_points:number("0.00")}',
        '      <span class="grade"> ({grade})</span>',
        '      <tpl if="is_passing_grade"> <span class="passing_grade">passed</span></tpl>',
        '      <tpl if="!is_passing_grade"> <span class="not_passing_grade">failed</span></tpl>',
        '   </tpl>',
        '</tpl>',
        '<tpl if="!has_feedback">',
        '   <span class="nofeedback">No feedback</span>',
        '</tpl>'
    ),

    selectedStudentTitleTpl: Ext.create('Ext.XTemplate',
        '{full_name} ({username})'
    ),

    loadData: function() {
        this.loader.requireCompleteDataset(function() {
            this.refreshView();
        }, this);
    },

    getGridColumns: function() {
        var gridColumns = this.callParent();
        gridColumns.push({
            flex: 1,
            xtype: 'numbercolumn',
            format: '0.00',
            text: 'Total points',
            menuDisabled: true,
            dataIndex: 'totalScaledPoints',
            minWidth: 80,
            sortable: true
        });
        var me = this;
        Ext.each(this.loader.assignment_store.data.items, function(assignmentRecord, index) {
            var assignment_id = assignmentRecord.get('id');
            var scaledPointdataIndex = assignment_id + '::scaledPoints';
            gridColumns.push({
                text: assignmentRecord.get('short_name'),
                dataIndex: scaledPointdataIndex,
                flex: 1,
                minWidth: 140,
                menuDisabled: true,
                sortable: true,
                renderer: function(scaled_points, p, studentRecord) {
                    var group = studentRecord.groupsByAssignmentId[assignment_id];
                    if(group.groupInfo) {
                        var tpldata = {
                            scaled_points: scaled_points,
                            is_open: group.groupInfo.is_open,
                            has_feedback: false
                        };
                        if(group.groupInfo.feedback !== null) {
                            Ext.apply(tpldata, {
                                has_feedback: true,
                                is_passing_grade: group.groupInfo.feedback.is_passing_grade,
                                grade: group.groupInfo.feedback.grade
                            });
                        }
                        var result = me.cellTpl.apply(tpldata);
                        return result;
                    } else {
                        return '';
                    }
                }
            });
        }, this);
        return gridColumns;
    },

    createLayout: function() {
        var grid = this.createGrid({
            region: 'center',
            listeners: {
                scope: this,
                select: this._onSelectStudent
            }
        });
        this._detailsPanel = Ext.widget('panel', {
            title: 'Select a student to view their details',
            region: 'south',
            autoScroll: true,
            layout: 'fit',
            height: 200,
            collapsed: true,
            collapsible: true
        });
        this.add({
            xtype: 'container',
            layout: 'border',
            items: [grid, this._detailsPanel]
        });
        //this.up('statistics-dataview').on('selectStudent', this._onSelectStudent, this);
    },

    _onSelectStudent: function(grid, record) {
        this._detailsPanel.removeAll();
        var groupInfos = [];
        Ext.Object.each(record.groupsByAssignmentId, function(assignmentid, group) {
            if(group.groupInfo !== null) {
                groupInfos.push(group.groupInfo);
            }
        }, this);
        this._detailsPanel.setTitle(this.selectedStudentTitleTpl.apply(record.data));
        this._detailsPanel.add({
            xtype: 'statistics-overviewofsinglestudent',
            assignment_store: record.assignment_store,
            groupInfos: groupInfos,
            username: record.get('username'),
            full_name: record.get('full_name'),
            labels: record.get('labels')
        });
        this._detailsPanel.expand();
    }
});
