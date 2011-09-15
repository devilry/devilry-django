Ext.define('devilry.statistics.Loader', {
    extend: 'Ext.util.Observable',

    constructor: function(periodid, config) {
        this.assignments = {};
        this.loadPeriod(periodid);

        this.addEvents('loaded');

        // Copy configured listeners into *this* object so that the base class's
        // constructor will add them.
        this.listeners = config.listeners;

        this.callParent(arguments);        
    },

    loadGroups: function(assignmentid, totalAssignments) {
        assignmentgroup_store.pageSize = 10000; // TODO: avoid UGLY hack
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
                this._tmpAssignmentsWithAllGroupsLoaded ++;
                if(this._tmpAssignmentsWithAllGroupsLoaded == totalAssignments) {
                    this.fireEvent('loaded', this);
                }
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

                this._tmpAssignmentsWithAllGroupsLoaded = 0;
                Ext.each(assignmentrecords, function(assignmentrecord, index) {
                    this.assignments[assignmentrecord.data.id] = {
                        record: assignmentrecord,
                        groups: undefined
                    }
                    this.loadGroups(assignmentrecord.data.id, assignmentrecords.length);
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
