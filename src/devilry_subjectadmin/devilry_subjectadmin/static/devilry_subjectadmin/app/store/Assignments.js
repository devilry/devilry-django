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

    _toMixedCollection: function() {
        var collection = new Ext.util.MixedCollection();
        this.each(function(assignmentRecord) {
            collection.add(assignmentRecord.get('id'), assignmentRecord);
        }, this);
        return collection;
    },

    getFirstRecordWithFirstDeadline: function() {
        var record = undefined;
        this.each(function(assignmentRecord) {
            var first_deadline = assignmentRecord.get('first_deadline');
            if(first_deadline) {
                record = assignmentRecord;
                return false; // break
            }
        }, this);
        return record;
    },

    findMostCommonFirstDeadlineDayDifference: function() {
        var assignments = this._toMixedCollection();
        var isoDateTime = function(dateobj) {
            if(Ext.isEmpty(dateobj)) {
                return '';
            }
            return Ext.Date.format(dateobj, 'Y-m-dTH:i');
        };
        assignments.sortBy(function(a, b) {
            return isoDateTime(a.get('first_deadline')).localeCompare(isoDateTime(b.get('first_deadline')));
        });

        var previousAssignmentRecord = null;
        var diffs = new Ext.util.MixedCollection();
        var countedAssignments = 0;
        assignments.each(function(assignmentRecord) {
            var currentDeadline = assignmentRecord.get('first_deadline');
            if(!Ext.isEmpty(currentDeadline)) { // NOTE: Skip first_deadline==null
                if(previousAssignmentRecord) {
                    var previousDeadline = previousAssignmentRecord.get('first_deadline');
                    var diff = currentDeadline.getTime() - previousDeadline.getTime();
                    var daysDiff = Math.round(diff / 86400000);
                    if(diffs.containsKey(daysDiff)) {
                        diffs.add(daysDiff, diffs.getByKey(daysDiff) + 1);
                    } else {
                        diffs.add(daysDiff, 1);
                    }
                    countedAssignments ++;
                }
                previousAssignmentRecord = assignmentRecord;
            }
        }, this);
        if(countedAssignments < 2) {
            return null;
        }

        diffs.sortBy(function(a, b) {
            return b - a; // Sort with largest number first
        });
        var mostCommonDayDiff = diffs.keys[0];
        return mostCommonDayDiff;
    }
});
