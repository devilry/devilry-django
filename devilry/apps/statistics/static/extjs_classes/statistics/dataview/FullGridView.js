Ext.define('devilry.statistics.dataview.FullGridView', {
    extend: 'devilry.statistics.dataview.MinimalGridView',
    cellTpl: Ext.create('Ext.XTemplate',
        '<tpl if="has_feedback">',
        '   {scaled_points:number("0.00")}',
        '   <tpl if="!is_passing_grade"> <span class="not_passing_grade">failed</span></tpl>',
        '</tpl>',
        '<tpl if="!has_feedback">',
        '   <span class="nofeedback">No feedback</span>',
        '</tpl>'
    ),

    _getGridColumns: function() {
        var gridColumns = this.callParent();
        gridColumns.push({
            flex: 1,
            xtype: 'numbercolumn',
            format: '0.00',
            text: 'Total points',
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
                minWidth: 80,
                sortable: true,
                renderer: function(scaled_points, p, studentRecord) {
                    var group = studentRecord.groupsByAssignmentId[assignment_id];
                    if(group.assignmentGroupRecord) {
                        return me.cellTpl.apply({
                            scaled_points: scaled_points,
                            has_feedback: group.assignmentGroupRecord.get('feedback') != null,
                            is_passing_grade: group.assignmentGroupRecord.get('feedback__is_passing_grade')
                        });
                    } else {
                        return '';
                    }
                }
            });
        }, this);
        return gridColumns;
    }
});
