Ext.define('devilry.statistics.ExtjsBridgeForLoader', {
    config: {
        loader: undefined
    },
    constructor: function(config) {
        this.initConfig(config);
    },

    /**
     * @private
     */
    _extjsFormatSingleAssignment: function(studentStoreFmt, assignment_id, group, storeFields, gridColumns) {
        var pointdataIndex = assignment_id + '::points';
        var scaledPointdataIndex = assignment_id + '::scaledPoints';
        var passingdataIndex = assignment_id + '::is_passing_grade';
        studentStoreFmt[pointdataIndex] = group.points;
        studentStoreFmt[scaledPointdataIndex] = group.scaled_points;
        studentStoreFmt[passingdataIndex] = group.is_passing_grade;

        if(!Ext.Array.contains(storeFields, pointdataIndex)) {
            storeFields.push(pointdataIndex);
            storeFields.push(scaledPointdataIndex);
            storeFields.push(passingdataIndex);
            gridColumns.push({
                //text: group.assignment_shortname,
                text: Ext.String.format('{0} (id: {1})', group.assignment_shortname, assignment_id),
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

    extjsFormat: function() {
        var storeStudents = [];
        var storeFields = ['username', 'labels'];
        var pointsTpl = Ext.create('Ext.XTemplate',
            '<ul class="labels-list">',
            '    <tpl for="labels">',
            '       <li class="label-{.}">{.}</li>',
            '    </tpl>',
            '</ul>'
        );
        var gridColumns = [{
            header: 'Username', dataIndex: 'username'
        }, {
            header: 'Labels', dataIndex: 'labels',
            renderer: function(value, p, record) {
                return pointsTpl.apply(record.data);
            }
        }];
        Ext.Object.each(this.loader._students, function(username, student, index) {
            var studentStoreFmt = {username: username};
            storeStudents.push(studentStoreFmt);
            Ext.Object.each(student.groupsByAssignmentId, function(assignment_id, group, index) {
                this._extjsFormatSingleAssignment(studentStoreFmt, assignment_id, group, storeFields, gridColumns);
            }, this);

            studentStoreFmt['labels'] = Ext.Object.getKeys(student.labels);
        }, this);
        return {
            storeStudents: storeStudents,
            storeFields: storeFields,
            gridColumns: gridColumns
        };
    },
});
