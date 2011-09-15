Ext.define('devilry.statistics.Loader', {
    constructor: function(periodid) {
        this.assignments = {};
        this.loadPeriod(periodid);
    },

    loadGroups: function(assignmentid) {
        assignmentgroup_store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: assignmentid
        }]);
        assignmentgroup_store.load({
            scope: this,
            callback: function(grouprecords, success) {
                console.log('Loaded assignmentgroups:', grouprecords);
                this.assignments[assignmentid].groups = grouprecords;
            }
        });
    },

    loadAssignments: function(periodid) {
        assignment_store.pageSize = 10000; // TODO: avoid UGLY hack
        console.log(periodid);

        assignment_store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: periodid
        }]);
        assignment_store.load({
            scope: this,
            callback: function(assignmentrecords, success) {
                console.log('Loaded assignments:', assignmentrecords);
                Ext.each(assignmentrecords, function(assignmentrecord, index) {
                    this.assignments[assignmentrecord.data.id] = {
                        record: assignmentrecord,
                        groups: undefined
                    }
                    this.loadGroups(assignmentrecord.data.id);
                }, this);
            }
        });
    },

    loadPeriod: function(periodid) {
        period_model.load(periodid, {
            scope: this,
            success: function(record) {
                console.log("Loaded period:", record);
                this.loadAssignments(record.data.id);
            }
        });
    }
});
