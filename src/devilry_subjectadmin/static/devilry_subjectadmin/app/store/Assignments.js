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
     * Get assignments with ``record(fieldname)!==null`` as a MixedCollection
     * sorted by ``fieldname``, with the oldest ``fieldname`` first.
     */
    _getAsMixedCollectionSortedByDateField: function(fieldname) {
        var assignments = new Ext.util.MixedCollection();
        this.each(function(assignmentRecord) {
            if(!Ext.isEmpty(assignmentRecord.get(fieldname))) {
                assignments.add(assignmentRecord.get('id'), assignmentRecord);
            }
        }, this);
        assignments.sortBy(function(a, b) {
            return a.get(fieldname).getTime() - b.get(fieldname).getTime();
        });
        return assignments;
    },

    /**
     * Find the most common timespan between first_deadline of all assignments
     * in the store.
     */
    _findMostCommonDayDifference: function(assignments, fieldname) {
        var previousAssignmentRecord = null;
        var diffs = new Ext.util.MixedCollection();
        assignments.each(function(assignmentRecord) {
            var current = assignmentRecord.get(fieldname);
            if(previousAssignmentRecord) {
                var previous = previousAssignmentRecord.get(fieldname);
                var diff = current.getTime() - previous.getTime();
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

    _smartAutodetectDateFieldValue: function(fieldname) {
        var assignments = this._getAsMixedCollectionSortedByDateField(fieldname);
        if(assignments.length < 2) {
            return null;
        }
        var mostCommonDayDiff = this._findMostCommonDayDifference(assignments, fieldname);
        if(mostCommonDayDiff === null) {
            return null;
        }

        var lastAssignment = assignments.last();
        var maxDelayCount = 1;
        if(mostCommonDayDiff.matchedAssignments > 1 && mostCommonDayDiff.days < 16) { // NOTE: matchedAssignments==2 means that we have 3 assignments (the first + the matches)
            maxDelayCount = 3; // We allow for a short vacation and still autodetect weekly and bi-weekly deliveries.
        }
        var delayCount = 1;
        var detectedDateTime = null;
        var previous_deadline = lastAssignment.get(fieldname);
        while(delayCount <= maxDelayCount) {
            var deadline = Ext.Date.add(previous_deadline, Ext.Date.DAY, mostCommonDayDiff.days*delayCount);
            var now = new Date();
            if(deadline > now) {
                detectedDateTime = deadline;
                break;
            }
            delayCount++;
        }
        if(detectedDateTime === null) {
            return null;
        }
        
        return {
            mostCommonDayDiff: mostCommonDayDiff,
            detectedDateTime: detectedDateTime,
            lastAssignment: lastAssignment,
            delayCount: delayCount
        };
    },

    smartAutodetectFirstDeadline: function() {
        return this._smartAutodetectDateFieldValue('first_deadline');
    },

    smartAutodetectPublishingTime: function() {
        return this._smartAutodetectDateFieldValue('publishing_time');
    },




    _sameDateTimeIgnoreSeconds: function(a, b) {
        return a.getYear() === b.getYear() && a.getMonth() === b.getMonth() &&
            a.getDay() === b.getDay() && a.getMinutes() === b.getMinutes();
    },

    /**
     * Get a publishing time that is:
     * - In the future.
     * - After the last published assignment by at least 2 minutes.
     */
    getUniqueFuturePublishingTime: function() {
        var assignments = this._getAsMixedCollectionSortedByDateField('publishing_time');
        var now = new Date();
        var lastAssignment = assignments.last();
        if(lastAssignment) {
            var last_pubtime = lastAssignment.get('publishing_time');
            if(now < last_pubtime || this._sameDateTimeIgnoreSeconds(last_pubtime, now)) {
                return Ext.Date.add(last_pubtime, Ext.Date.MINUTE, 2); // NOTE: We add 2 minutes to avoid that this assignment gets the same pubtime as the last assignment when the seconds are removed.
            }
        }
        return now;
    }
});
