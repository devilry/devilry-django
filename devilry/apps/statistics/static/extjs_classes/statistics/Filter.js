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
        Ext.each(this.must_pass, function(assignment_short_name, index) {
            var assignment = student.assignments[assignment_short_name];
            if(!assignment) {
                throw "Invalid assignment name: " + assignment_short_name;
            }
            if(!assignment.is_passing_grade) {
                matches = false;
                return false; // Break
            }
        }, this);
        return matches;
    },

    _matchPointspec: function(student) {
        if(!this.pointspec) {
            return true;
        }
        return this.pointspec.match(student);
    }

});
