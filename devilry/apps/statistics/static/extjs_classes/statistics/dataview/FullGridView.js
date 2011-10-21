Ext.define('devilry.statistics.dataview.FullGridView', {
    extend: 'devilry.statistics.dataview.MinimalGridView',

    _extjsFormatSingleAssignment: function(studentStoreFmt, assignment_id, group) {
        var pointdataIndex = assignment_id + '::points';
        var scaledPointdataIndex = assignment_id + '::scaledPoints';
        var passingdataIndex = assignment_id + '::is_passing_grade';
        studentStoreFmt[pointdataIndex] = group.points;
        studentStoreFmt[scaledPointdataIndex] = group.scaled_points;
        studentStoreFmt[passingdataIndex] = group.is_passing_grade;

        if(!Ext.Array.contains(this.storeFields, pointdataIndex)) {
            this.storeFields.push(pointdataIndex);
            this.storeFields.push(scaledPointdataIndex);
            this.storeFields.push(passingdataIndex);
            this.gridColumns.push({
                text: group.assignment_shortname,
                //text: Ext.String.format('{0} (id: {1})', group.assignment_shortname, assignment_id),
                columns: [{
                    dataIndex: scaledPointdataIndex,
                    text: 'Scaled points',
                    sortable: true
                }, {
                    dataIndex: passingdataIndex,
                    text: 'Is passing grade',
                    sortable: true
                }]
            });
        }
    },

    _extraOnEachStudent: function(student, studentStoreFmt) {
        Ext.Object.each(student.groupsByAssignmentId, function(assignment_id, group, index) {
            this._extjsFormatSingleAssignment(studentStoreFmt, assignment_id, group);
        }, this);
    },
});
