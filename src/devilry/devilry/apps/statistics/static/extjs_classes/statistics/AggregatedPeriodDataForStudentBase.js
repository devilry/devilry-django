Ext.define('devilry.statistics.AggregatedPeriodDataForStudentBase', {
    extend: 'Ext.data.Model',

    /**
     * @property {Object} [assignment_store]
     * Used to calculate scaled points.
     */

    hasLabel: function(label) {
        return Ext.Array.some(this.get('labels'), function(labelItem) {
            return labelItem.label === label;
        });
    },

    getLabelId: function(label) {
        var labels = this.get('labels');
        for(var index=0; index<labels.length; index++)  {
            var labelItem = labels[index];
            if(labelItem.label === label) {
                return labelItem.id;
            }
        }
        return -1;
    },

    countPassingAssignments: function(assignment_ids) {
        var passes = 0;
        Ext.Object.each(this.groupsByAssignmentId, function(assignment_id, group) {
            if(group.groupInfo && Ext.Array.contains(assignment_ids, parseInt(assignment_id, 10))) {
                var feedback = group.groupInfo.feedback;
                if(feedback !== null && feedback.is_passing_grade) {
                    passes ++;
                }
            }
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
            if(Ext.Array.contains(assignment_ids, parseInt(assignment_id, 10))) {
                sumScaledPoints += group.scaled_points;
            }
        }, this);
        return sumScaledPoints;
    },

    updateScaledPoints: function() {
        var assignment_ids = Ext.Object.getKeys(this.groupsByAssignmentId);
        var totalScaledPoints = 0;
        Ext.each(this.assignment_ids, function(assignment_id, index) {
            var group = this.groupsByAssignmentId[assignment_id];
            if(group.groupInfo) {
                group.scaled_points = this._calculateScaledPoints(group.groupInfo);
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

    _calculateScaledPoints: function(groupInfo) {
        if(groupInfo && groupInfo.feedback) {
            var assignmentRecord = this.assignment_store.getById(groupInfo.assignment_id);
            var points = groupInfo.feedback.points;
            return assignmentRecord.get('scale_points_percent') * points / 100;
        } else {
            return 0;
        }
    }
});
