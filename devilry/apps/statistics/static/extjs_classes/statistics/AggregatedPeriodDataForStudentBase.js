Ext.define('devilry.statistics.AggregatedPeriodDataForStudentBase', {
    extend: 'Ext.data.Model',

    constructor: function(assignment_store, config) {
        this.callParent([config]);
        this.assignment_store = assignment_store;
        this.updateScaledPoints();
    },

    setLabel: function(label, value) {
        var labels = this.get('labels');
        labels[label] = value;
        this.set('labels', labels);
        this.set('labelKeys', Ext.Object.getKeys(labels));
    },

    delLabel: function(label) {
        var labels = this.get('labels');
        delete labels[label];
        this.set('labels', labels);
        this.set('labelKeys', Ext.Object.getKeys(labels));
    },

    passesAssignments: function(assignment_ids) {
        var passes = 0;
        Ext.Object.each(this.get('groupsByAssignmentId'), function(assignment_id, group) {
            if(Ext.Array.contains(assignment_ids, parseInt(assignment_id))) {
                if(group.is_passing_grade) {
                    passes ++;
                }
            };
        }, this);
        return passes === assignment_ids.length;
    },

    getSumScaledPoints: function(assignment_ids) {
        var sumScaledPoints = 0;
        Ext.Object.each(this.get('groupsByAssignmentId'), function(assignment_id, group) {
            if(Ext.Array.contains(assignment_ids, parseInt(assignment_id))) {
                sumScaledPoints += group.scaled_points;
            };
        }, this);
        return sumScaledPoints;
    },

    updateScaledPoints: function() {
        var assignment_ids = Ext.Object.getKeys(this.get('groupsByAssignmentId'));
        var totalScaledPoints = 0;
        Ext.each(assignment_ids, function(assignment_id, index) {
            var group = this.get('groupsByAssignmentId')[parseInt(assignment_id)];
            group.scaled_points = this._calculateScaledPoints(group);
            this.set(assignment_id + '::scaledPoints', group.scaled_points);
            totalScaledPoints += group.scaled_points;
        }, this);
        this.set('totalScaledPoints', totalScaledPoints);
        this.commit(); // NOTE: removes the red triangle from grid
    },

    hasMinimalNumberOfScaledPointsOn: function(assignment_ids, minimumScaledPoints) {
        return this.getSumScaledPoints(assignment_ids) >= minimumScaledPoints;
    },

    getScaledPoints: function(assignment_id) {
        var group = this.get('groupsByAssignmentId')[assignment_id];
        return group.scaled_points;
    },

    _calculateScaledPoints: function(group) {
        var assignmentRecord = this.assignment_store.getById(group.parentnode);
        return assignmentRecord.get('scale_points_percent') * group.points / 100;
    }
});
