Ext.define('devilry.statistics.Filter', {
    config: {
        pointspec: undefined,
        must_pass: []
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    match: function(student) {
        return this._matchIsPassingGrade(student) && this._matchPointspec(student);
    },

    _matchIsPassingGrade: function(student) {
        if(this.must_pass.length === 0) {
            return true;
        }
        var matches = true;
        Ext.each(this.must_pass, function(assignment_ids, index) {
            var one_of_them_is_passing = this._passesOneOfManyAssignments(student, assignment_ids);
            if(!one_of_them_is_passing) {
                matches = false;
                return false; // Break
            }
        }, this);
        return matches;
    },

    _passesOneOfManyAssignments: function(student, assignment_ids) {
        var one_of_them_is_passing = false;
        Ext.each(assignment_ids, function(assignment_id, index) {
            var group = student.groupsByAssignmentId[assignment_id];
            if(group) {
                if(group.is_passing_grade) {
                    one_of_them_is_passing = true;
                    return false; // Break
                }
            }
        }, this);
        return one_of_them_is_passing;
    },

    _matchPointspec: function(student) {
        if(!this.pointspec) {
            return true;
        }
        return this.pointspec.match(student);
    }

});
