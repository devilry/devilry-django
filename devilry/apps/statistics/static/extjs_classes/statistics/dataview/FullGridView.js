Ext.define('devilry.statistics.dataview.FullGridView', {
    extend: 'devilry.statistics.dataview.MinimalGridView',
    cellTpl: Ext.create('Ext.XTemplate',
        '{scaled_points}',
        '<tpl if="!is_passing_grade"> <span class="not_passing_grade">failed</span></tpl>'
    ),

    _getGridColumns: function() {
        var gridColumns = this.callParent();
        var me = this;
        Ext.each(this.loader.assignment_store.data.items, function(assignmentRecord, index) {
            var assignment_id = assignmentRecord.get('id');
            var scaledPointdataIndex = assignment_id + '::scaledPoints';
            gridColumns.push({
                text: assignmentRecord.get('short_name'),
                dataIndex: scaledPointdataIndex,
                sortable: true,
                renderer: function(value, p, record) {
                    var group = record.get(assignment_id);
                    return me.cellTpl.apply({
                        scaled_points: me.loader.calculateScaledPoints(group),
                        is_passing_grade: group.is_passing_grade
                    });
                }
            });
        }, this);
        return gridColumns;
    }
});
