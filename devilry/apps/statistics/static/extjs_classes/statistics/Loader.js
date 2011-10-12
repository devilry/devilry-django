Ext.define('devilry.statistics.Loader', {
    extend: 'Ext.util.Observable',

    constructor: function(periodid, config) {
        this.storeFields = ['username', 'assignments'];
        this.gridColumns = [{header: 'Username', dataIndex: 'username'}];
        this._studentsUsernameToIndexMap = {};
        this.studentsStoreFmt = [];
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
                        var studentStoreFmt;
                        if(this._studentsUsernameToIndexMap[username]) {
                            studentStoreFmt = this.studentsStoreFmt[this._studentsUsernameToIndexMap[username].index];
                        } else {
                            this._studentsUsernameToIndexMap[username] = {index: this.studentsStoreFmt.length};
                            studentStoreFmt = {};
                            studentStoreFmt.username = username;
                            this.studentsStoreFmt.push(studentStoreFmt);
                        }

                        var assignment_ident = grouprecord.data.parentnode__short_name;
                        var pointdataIndex = assignment_ident + '::points';
                        var scaledPointdataIndex = assignment_ident + '::scaledPoints';
                        var passingdataIndex = assignment_ident + '::is_passing_grade';
                        if(!studentStoreFmt.assignments) {
                            studentStoreFmt.assignments = {};
                        }
                        studentStoreFmt.assignments[assignment_ident] = {
                            points: grouprecord.data.feedback__points,
                            scaled_points: grouprecord.data.feedback__points,
                            is_passing_grade: grouprecord.data.feedback__is_passing_grade
                        };
                        studentStoreFmt[pointdataIndex] = grouprecord.data.feedback__points;
                        studentStoreFmt[scaledPointdataIndex] = grouprecord.data.feedback__points;
                        studentStoreFmt[passingdataIndex] = grouprecord.data.feedback__is_passing_grade;

                        if(!Ext.Array.contains(this.storeFields, pointdataIndex)) {
                            this.storeFields.push(pointdataIndex);
                            this.storeFields.push(scaledPointdataIndex);
                            this.storeFields.push(passingdataIndex);
                            this.gridColumns.push({
                                text: assignment_ident,
                                columns: [{
                                    dataIndex: scaledPointdataIndex,
                                    text: 'Points',
                                    sortable: true
                                }, {
                                    dataIndex: passingdataIndex,
                                    text: 'Is passing grade',
                                    sortable: true
                                }]
                            });
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
    },

    //extjsFormat: function() {
        //Ext.each(this.students, function(student, index) {
            //Ext.each(student.assignments, function(assignment, index) {
                
            //}, this);
        //}, this);
    //}
});
