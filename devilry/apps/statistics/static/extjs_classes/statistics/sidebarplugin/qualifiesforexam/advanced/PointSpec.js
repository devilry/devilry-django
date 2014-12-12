Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec', {
    config: {
        assignments: [],
        min: undefined,
        max: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        if(Ext.typeOf(this.min) == 'number' && Ext.typeOf(this.max) == 'number' && this.min > this.max) {
            throw "Minimum points must be less than maximum points.";
        }
    },


    match: function(student) {
        var tot_scaled_points = 0;
        Ext.each(this.assignments, function(assignment_ids, index) {
            tot_scaled_points += this._findAssignmentWithMostScaledPoints(student, assignment_ids);
        }, this);
        //console.log(student.username, this.assignments, tot_scaled_points);
        if(this.min !== undefined && tot_scaled_points < this.min) {
            return false;
        }
        if(this.max !== undefined && tot_scaled_points > this.max) {
            return false;
        }
        return true;
    },

    _findAssignmentWithMostScaledPoints: function(student, assignment_ids) {
        var max = 0;
        Ext.each(assignment_ids, function(assignment_id, index) {
            var group = student.groupsByAssignmentId[assignment_id];
            var scaled_points = student.getScaledPoints(assignment_id);
            if(max < scaled_points) {
                max = scaled_points;
            }
        });
        return max;
    },

    toExportObject: function() {
        return {
            assignments: this.assignments,
            min: this.min,
            max: this.max
        };
    }
});
