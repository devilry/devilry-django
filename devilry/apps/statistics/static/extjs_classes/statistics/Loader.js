Ext.define('devilry.statistics.Loader', {
    extend: 'Ext.util.Observable',

    constructor: function(periodid, config) {
        this.fields = ['username'];
        this.columns = [{header: 'Username', dataIndex: 'username'}];
        this.studentsMap = {};
        this.students = [];
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
                //console.log('Loaded assignmentgroups:', grouprecords);
                Ext.each(grouprecords, function(grouprecord, index) {
                    Ext.each(grouprecord.data.candidates__student__username, function(username, index) {
                        var student;
                        if(this.studentsMap[username]) {
                            student = this.students[this.studentsMap[username]];
                        } else {
                            this.studentsMap[username] = this.students.length;
                            student = {};
                            student.username = username;
                            this.students.push(student);
                        }

                        var assignment_ident = grouprecord.data.parentnode__short_name;
                        var pointdataIndex = assignment_ident + '_points';
                        var passingdataIndex = assignment_ident + '_is_passing_grade';
                        student[pointdataIndex] = grouprecord.data.feedback__points;
                        student[passingdataIndex] = grouprecord.data.feedback__is_passing_grade;

                        if(!Ext.Array.contains(this.fields, pointdataIndex)) {
                            this.fields.push(pointdataIndex);
                            this.fields.push(passingdataIndex);
                            this.columns.push({dataIndex: pointdataIndex, header: pointdataIndex});
                            this.columns.push({dataIndex: passingdataIndex, header: passingdataIndex});
                            this.columns.push({dataIndex: passingdataIndex, header: passingdataIndex});
                        }
                    }, this);
                }, this);

                this._tmpAssignmentsWithAllGroupsLoaded ++;
                if(this._tmpAssignmentsWithAllGroupsLoaded == totalAssignments) {
                    this.fireEvent('loaded', this);
                }
            }
        });
    },

    loadAssignments: function(periodid) {
        assignment_store.pageSize = 10000; // TODO: avoid UGLY hack
        assignment_store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: periodid
        }]);
        assignment_store.load({
            scope: this,
            callback: function(assignmentrecords, success) {
                //console.log('Loaded assignments:', assignmentrecords);
                this._tmpAssignmentsWithAllGroupsLoaded = 0;
                Ext.each(assignmentrecords, function(assignmentrecord, index) {
                    this.loadGroups(assignmentrecord.data.id, assignmentrecords.length);
                }, this);
            }
        });
    },

    loadPeriod: function(periodid) {
        period_model.load(periodid, {
            scope: this,
            success: function(record) {
                //console.log("Loaded period:", record);
                this.loadAssignments(record.data.id);
            }
        });
    }
});
