Ext.define('devilry.statistics.dataview.FullGridView', {
    extend: 'devilry.statistics.dataview.MinimalGridView',
    cellTpl: Ext.create('Ext.XTemplate',
        '{scaled_points:number("0.00")}',
        '<tpl if="!is_passing_grade"> <span class="not_passing_grade">failed</span></tpl>'
    ),

    _getGridColumns: function() {
        var gridColumns = this.callParent();
        gridColumns.push({
            xtype: 'numbercolumn',
            format: '0.00',
            text: 'Total points',
            dataIndex: 'totalScaledPoints',
            sortable: true
        });
        var me = this;
        Ext.each(this.loader.assignment_store.data.items, function(assignmentRecord, index) {
            var assignment_id = assignmentRecord.get('id');
            var scaledPointdataIndex = assignment_id + '::scaledPoints';
            gridColumns.push({
                text: assignmentRecord.get('short_name'),
                dataIndex: scaledPointdataIndex,
                sortable: true,
                renderer: function(scaled_points, p, studentRecord) {
                    var group = studentRecord.groupsByAssignmentId[assignment_id];
                    if(group) {
                        return me.cellTpl.apply({
                            scaled_points: scaled_points,
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
