Ext.define('devilry_subjectadmin.store.Assignments', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.Assignment',

    loadAssignmentsInPeriod: function(period_id, callbackFn, callbackScope) {
        this.proxy.extraParams.parentnode = period_id;
        this.load({
            scope: callbackScope,
            callback: callbackFn
        });
    },

    getFirstRecordWithFirstDeadline: function() {
        var record;
        this.each(function(assignmentRecord) {
            var first_deadline = assignmentRecord.get('first_deadline');
            if(first_deadline) {
                record = assignmentRecord;
                return false; // break
            }
        }, this);
        return record;
    },

    /**
     * Get assignments with ``first_deadline!==null`` as a MixedCollection
     * sorted by first deadline, with the oldest first deadline first.
     */
    _getAsMixedCollectionSortedByFirstDeadline: function() {
        var assignments = new Ext.util.MixedCollection();
        this.each(function(assignmentRecord) {
            if(!Ext.isEmpty(assignmentRecord.get('first_deadline'))) {
                assignments.add(assignmentRecord.get('id'), assignmentRecord);
            }
        }, this);

        var isoDateTime = function(dateobj) {
            if(Ext.isEmpty(dateobj)) {
                return '';
            }
            return Ext.Date.format(dateobj, 'Y-m-dTH:i');
        };
        assignments.sortBy(function(a, b) {
            return isoDateTime(a.get('first_deadline')).localeCompare(isoDateTime(b.get('first_deadline')));
        });
        return assignments;
    },

    /**
     * Find the most common timespan between first_deadline of all assignments
     * in the store.
     */
    _findMostCommonFirstDeadlineDayDifference: function(assignments) {
        var previousAssignmentRecord = null;
        var diffs = new Ext.util.MixedCollection();
        assignments.each(function(assignmentRecord) {
            var currentDeadline = assignmentRecord.get('first_deadline');
            if(previousAssignmentRecord) {
                var previousDeadline = previousAssignmentRecord.get('first_deadline');
                var diff = currentDeadline.getTime() - previousDeadline.getTime();
                var daysDiff = Math.round(diff / 86400000);
                if(diffs.containsKey(daysDiff)) {
                    diffs.add(daysDiff, diffs.getByKey(daysDiff) + 1);
                } else {
                    diffs.add(daysDiff, 1);
                }
            }
            previousAssignmentRecord = assignmentRecord;
        }, this);

        diffs.sortBy(function(a, b) {
            return b - a; // Sort with largest number first
        });
        var mostCommonDayDiff = diffs.keys[0];
        return {
            days: mostCommonDayDiff,
            matchedAssignments: diffs.getByKey(mostCommonDayDiff)
        };
    },

    smartAutodetectFirstDeadline: function() {
        var assignments = this._getAsMixedCollectionSortedByFirstDeadline();
        if(assignments.length < 2) {
            return null;
        }
        var mostCommonDayDiff = this._findMostCommonFirstDeadlineDayDifference(assignments);
        var lastAssignment = assignments.last();
        var maxDelayCount = 1;
        if(mostCommonDayDiff.matchedAssignments > 1 && mostCommonDayDiff.days < 16) { // NOTE: matchedAssignments==2 means that we have 3 assignments (the first + the matches)
            maxDelayCount = 3; // We allow for a short vacation and still autodetect weekly and bi-weekly deliveries.
        }

        var delayCount = 1;
        var first_deadline = null;
        var previous_deadline = lastAssignment.get('first_deadline');
        while(delayCount <= maxDelayCount) {
            var deadline = Ext.Date.add(previous_deadline, Ext.Date.DAY, mostCommonDayDiff.days*delayCount);
            var now = new Date();
            if(deadline > now) {
                first_deadline = deadline;
                break;
            }
            delayCount++;
        }
        if(first_deadline === null) {
            return null;
        }
        
        return {
            mostCommonDayDiff: mostCommonDayDiff,
            first_deadline: first_deadline,
            lastAssignment: lastAssignment,
            delayCount: delayCount
        };
    }
});
