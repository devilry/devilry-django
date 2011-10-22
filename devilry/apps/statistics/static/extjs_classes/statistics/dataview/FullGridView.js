Ext.define('devilry.statistics.dataview.FullGridView', {
    extend: 'devilry.statistics.dataview.MinimalGridView',
    cellTpl: Ext.create('Ext.XTemplate',
        '{scaled_points}',
        '<tpl if="!is_passing_grade"> <span class="not_passing_grade">failed</span></tpl>'
    ),

    _extjsFormatSingleAssignment: function(studentStoreFmt, assignment_id, group) {
        studentStoreFmt[assignment_id] = group;

        var scaledPointdataIndex = assignment_id + '::scaledPoints';
        studentStoreFmt[scaledPointdataIndex] = this.loader.calculateScaledPoints(group);

        var me = this;
        if(!Ext.Array.contains(this.storeFields, assignment_id)) {
            this.storeFields.push(assignment_id);
            this.storeFields.push(scaledPointdataIndex);
            this.gridColumns.push({
                text: group.assignment_shortname,
                //text: Ext.String.format('{0} (id: {1})', group.assignment_shortname, assignment_id),
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
        }
    },

    _extraOnEachStudent: function(student, studentStoreFmt) {
        Ext.Object.each(student.groupsByAssignmentId, function(assignment_id, group, index) {
            this._extjsFormatSingleAssignment(studentStoreFmt, assignment_id, group);
        }, this);
    },
});
