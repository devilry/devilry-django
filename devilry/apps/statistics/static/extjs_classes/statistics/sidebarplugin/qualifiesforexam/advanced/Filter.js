Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.Filter', {
    config: {
        pointspecArgs: undefined,
        must_pass: []
    },

    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec'
    ],

    strTpl: Ext.create('Ext.XTemplate',
        '<div style="white-space: normal">',
            '<tpl if="must_pass.length &gt; 0">',
                '<p>Must pass: ',
                    '<tpl for="must_pass">',
                        '(<tpl for=".">',
                            '{data.short_name}',
                            '<tpl if="xindex &lt; xcount"> OR </tpl>',
                        '</tpl>)',
                        '<tpl if="xindex &lt; xcount"> AND </tpl>',
                    '</tpl>',
                '</p>',
            '</tpl>',
            '<tpl if="pointassignments.length &gt; 0">',
                '<p>Must have between ',
                    '<tpl if="!min">0</tpl><tpl if="min">{min}</tpl>',
                    ' and ',
                    '<tpl if="!max">&#8734;</tpl><tpl if="max">{max}</tpl>',
                    ' points in total (including both ends) on ',
                    '<tpl for="pointassignments">',
                        '(',
                        '<tpl if="length &gt; 1">best of: </tpl>',
                        '<tpl for=".">',
                            '{data.short_name}',
                            '<tpl if="xindex &lt; xcount">, </tpl>',
                        '</tpl>)',
                        '<tpl if="xindex &lt; xcount"> AND </tpl>',
                    '</tpl>',
                '</p>',
            '</tpl>',
        '</div>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.pointspec = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec', this.pointspecArgs);
    },

    toReadableSummary: function(assignment_store) {
        var data = {
            must_pass: this._assignmentIdListToAssignmentRecords(assignment_store, this.must_pass),
            min: this.pointspec.min,
            max: this.pointspec.max,
            pointassignments: this._assignmentIdListToAssignmentRecords(assignment_store, this.pointspec.assignments)
        };
        return this.strTpl.apply(data);
    },

    _assignmentIdListToAssignmentRecords: function(assignment_store, arrayOfArrayOfassignmentIds) {
        var arrayOfArrayOfAssignmentRecords = [];
        Ext.each(arrayOfArrayOfassignmentIds, function(assignmentIds, index) {
            var assignmentRecords = [];
            Ext.each(assignmentIds, function(assignmentId, index) {
                var assignmentRecordIndex = assignment_store.findExact('id', assignmentId);
                var assignmentRecord = assignment_store.getAt(assignmentRecordIndex);
                assignmentRecords.push(assignmentRecord);
            });
            arrayOfArrayOfAssignmentRecords.push(assignmentRecords);
        });
        return arrayOfArrayOfAssignmentRecords;
    },

    match: function(studentRecord) {
        return this._matchIsPassingGrade(studentRecord) && this._matchPointspec(studentRecord);
    },

    _matchIsPassingGrade: function(studentRecord) {
        if(this.must_pass.length === 0) {
            return true;
        }
        var matches = true;
        Ext.each(this.must_pass, function(assignment_ids, index) {
            var one_of_them_is_passing = studentRecord.countPassingAssignments(assignment_ids) > 0;
            if(!one_of_them_is_passing) {
                matches = false;
                return false; // Break
            }
        }, this);
        return matches;
    },

    _matchPointspec: function(studentRecord) {
        if(!this.pointspec) {
            return true;
        }
        return this.pointspec.match(studentRecord);
    },

    toExportObject: function() {
        return {
            must_pass: this.must_pass,
            pointspecArgs: this.pointspec.toExportObject()
        };
    }
});
