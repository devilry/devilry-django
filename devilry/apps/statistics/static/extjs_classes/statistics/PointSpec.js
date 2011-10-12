Ext.define('devilry.statistics.PointSpec', {
    config: {
        assignments: [],
        min: undefined,
        max: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
    },


    match: function(student) {
        var tot_scaled_points = 0;
        Ext.each(this.assignments, function(assignment_short_name, index) {
            var assignment = student.assignments[assignment_short_name];
            if(!assignment) {
                throw "Invalid assignment name: " + assignment_short_name;
            }
            tot_scaled_points += assignment.scaled_points;
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
});
