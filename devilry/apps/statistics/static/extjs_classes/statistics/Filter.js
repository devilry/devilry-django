Ext.define('devilry.statistics.Filter', {
    config: {
        label: undefined,
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
        Ext.each(this.must_pass, function(assignment_short_names, index) {
            var one_of_them_is_passing = this._passesOneOfManyAssignments(student, assignment_short_names);
            if(!one_of_them_is_passing) {
                matches = false;
                return false; // Break
            }
        }, this);
        return matches;
    },

    _passesOneOfManyAssignments: function(student, assignment_short_names) {
        var one_of_them_is_passing = false;
        Ext.each(assignment_short_names, function(assignment_short_name, index) {
            var assignment = student.assignments[assignment_short_name];
            if(!assignment) {
                throw "Invalid assignment name: " + assignment_short_name;
            }
            if(assignment.is_passing_grade) {
                one_of_them_is_passing = true;
                return false; // Break
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
