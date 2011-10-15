Ext.define('devilry.statistics.PointSpec', {
    config: {
        assignments: [],
        min: undefined,
        max: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        if(this.min != undefined && this.max != undefined && this.min > this.max) {
            throw "Minimum points must be less than maximum points.";
        }
    },


    match: function(student) {
        var tot_scaled_points = 0;
        Ext.each(this.assignments, function(assignment_short_names, index) {
            tot_scaled_points += this._findAssignmentWithMostScaledPoints(student, assignment_short_names);
        }, this);
        //console.log(student.username, this.assignments, tot_scaled_points);
        if(this.min != undefined && tot_scaled_points < this.min) {
            return false;
        }
        if(this.max != undefined && tot_scaled_points > this.max) {
            return false;
        }
        return true;
    },

    _findAssignmentWithMostScaledPoints: function(student, assignment_short_names) {
        var max = 0;
        Ext.each(assignment_short_names, function(assignment_short_name, index) {
            var assignment = student.assignments[assignment_short_name];
            if(!assignment) {
                throw "Invalid assignment name: " + assignment_short_name;
            }
            if(max < assignment.scaled_points) {
                max = assignment.scaled_points;
            }
        });
        return max;
    }
});
