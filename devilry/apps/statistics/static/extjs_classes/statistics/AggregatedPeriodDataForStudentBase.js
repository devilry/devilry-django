Ext.define('devilry.statistics.AggregatedPeriodDataForStudentBase', {
    extend: 'Ext.data.Model',

    setLabel: function(label, value) {
        this.labels[label] = value;
        this.setLabelKeysFromLabels();
    },

    delLabel: function(label) {
        delete this.labels[label];
        this.setLabelKeysFromLabels();
    },

    setLabelKeysFromLabels: function() {
        this.set('labelKeys', Ext.Object.getKeys(this.labels));
        this.commit();
    },

    countPassingAssignments: function(assignment_ids) {
        var passes = 0;
        Ext.Object.each(this.groupsByAssignmentId, function(assignment_id, group) {
            if(group.assignmentGroupRecord && Ext.Array.contains(assignment_ids, parseInt(assignment_id))) {
                if(group.assignmentGroupRecord.get('feedback__is_passing_grade')) {
                    passes ++;
                }
            };
        }, this);
        return passes;
    },
    passesAssignments: function(assignment_ids) {
        return this.countPassingAssignments(assignment_ids) === assignment_ids.length;
    },

    passesAllAssignments: function() {
        return passesAssignments(this.assignment_ids);
    },

    getSumScaledPoints: function(assignment_ids) {
        var sumScaledPoints = 0;
        Ext.Object.each(this.groupsByAssignmentId, function(assignment_id, group) {
            if(Ext.Array.contains(assignment_ids, parseInt(assignment_id))) {
                sumScaledPoints += group.scaled_points;
            };
        }, this);
        return sumScaledPoints;
    },

    updateScaledPoints: function() {
        var assignment_ids = Ext.Object.getKeys(this.groupsByAssignmentId);
        var totalScaledPoints = 0;
        Ext.each(this.assignment_ids, function(assignment_id, index) {
            var group = this.groupsByAssignmentId[assignment_id];
            if(group.assignmentGroupRecord) {
                group.scaled_points = this._calculateScaledPoints(group.assignmentGroupRecord);
                this.set(assignment_id + '::scaledPoints', group.scaled_points);
                totalScaledPoints += group.scaled_points;
            }
        }, this);
        this.set('totalScaledPoints', totalScaledPoints);
        this.commit(); // NOTE: removes the red triangle from grid
    },

    hasMinimalNumberOfScaledPointsOn: function(assignment_ids, minimumScaledPoints) {
        return this.getSumScaledPoints(assignment_ids) >= minimumScaledPoints;
    },

    getScaledPoints: function(assignment_id) {
        var group = this.groupsByAssignmentId[assignment_id];
        if(group) {
            return group.scaled_points;
        } else {
            return 0;
        }
    },

    _calculateScaledPoints: function(assignmentGroupRecord) {
        if(assignmentGroupRecord) {
            var assignmentRecord = this.assignment_store.getById(assignmentGroupRecord.get('parentnode'));
            var points = assignmentGroupRecord.get('feedback__points');
            return assignmentRecord.get('scale_points_percent') * points / 100;
        } else {
            return 0;
        }
    }
});
