Ext.define('devilry.statistics.Loader', {
    extend: 'Ext.util.Observable',

    constructor: function(periodid, config) {
        this._studentsUsernameToIndexMap = {};
        this._students = {};
        this._assignmentCollection = Ext.create('Ext.util.MixedCollection');
        this._loadPeriod(periodid);

        this.addEvents('loaded');

        // Copy configured listeners into *this* object so that the base class's
        // constructor will add them.
        this.listeners = config.listeners;

        this.callParent(arguments);        
    },

    /**
     * @private
     */
    _loadPeriod: function(periodid) {
        period_model.load(periodid, {
            scope: this,
            success: function(record) {
                this._loadAssignments(record.data.id);
            }
        });
    },

    /**
     * @private
     */
    _loadAssignments: function(periodid) {
        assignment_store.pageSize = 10000; // TODO: avoid UGLY hack
        assignment_store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: periodid
        }]);
        assignment_store.load({
            scope: this,
            callback: this._onAssignmentsLoaded
        });
    },

    /**
     * @private
     */
    _onAssignmentsLoaded: function(assignmentrecords, success) {
        this._tmpAssignmentsWithAllGroupsLoaded = 0;
        Ext.each(assignmentrecords, function(assignmentrecord, index) {
            this._assignmentCollection.add(assignmentrecord.data.id, assignmentrecord);
            this._loadGroups(assignmentrecord.data.id, assignmentrecords.length);
        }, this);
    },

    /**
     * @private
     */
    _loadGroups: function(assignmentid, totalAssignments) {
        assignmentgroup_store.pageSize = 10000; // TODO: avoid UGLY hack
        assignmentgroup_store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: assignmentid
        }]);
        assignmentgroup_store.load({
            scope: this,
            callback: function(grouprecords, success) {
                this._onLoadGroups(totalAssignments, grouprecords, success);
            }
        });
    },

    /**
     * @private
     */
    _onLoadGroups: function(totalAssignments, grouprecords, success) {
        Ext.each(grouprecords, function(grouprecord, index) {
            Ext.each(grouprecord.data.candidates__student__username, function(username, index) {
                this._addStudent(username, grouprecord);
            }, this);
        }, this);

        this._tmpAssignmentsWithAllGroupsLoaded ++;
        if(this._tmpAssignmentsWithAllGroupsLoaded == totalAssignments) {
            this.fireEvent('loaded', this);
        }
    },

    /**
     * @private
     */
    _addStudent: function(username, grouprecord) {
        if(!this._students[username]) {
            this._students[username] = {
                username: username,
                assignments: {}
            };
        }
        var student = this._students[username];
        student.assignments[grouprecord.data.parentnode__short_name] = {
            points: grouprecord.data.feedback__points,
            scaled_points: grouprecord.data.feedback__points,
            is_passing_grade: grouprecord.data.feedback__is_passing_grade
        };
    },


    /**
     * @private
     */
    _extjsFormatSingleAssignment: function(studentStoreFmt, assignment_short_name, assignment, storeFields, gridColumns) {
        var pointdataIndex = assignment_short_name + '::points';
        var scaledPointdataIndex = assignment_short_name + '::scaledPoints';
        var passingdataIndex = assignment_short_name + '::is_passing_grade';
        studentStoreFmt[pointdataIndex] = assignment.points;
        studentStoreFmt[scaledPointdataIndex] = assignment.scaled_points;
        studentStoreFmt[passingdataIndex] = assignment.is_passing_grade;

        if(!Ext.Array.contains(storeFields, pointdataIndex)) {
            storeFields.push(pointdataIndex);
            storeFields.push(scaledPointdataIndex);
            storeFields.push(passingdataIndex);
            gridColumns.push({
                text: assignment_short_name,
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
    },

    extjsFormat: function() {
        var storeStudents = [];
        var storeFields = ['username'];
        var gridColumns = [{header: 'Username', dataIndex: 'username'}];
        Ext.Object.each(this._students, function(username, student, index) {
            var studentStoreFmt = {username: username};
            storeStudents.push(studentStoreFmt);
            Ext.Object.each(student.assignments, function(assignment_short_name, assignment, index) {
                this._extjsFormatSingleAssignment(studentStoreFmt, assignment_short_name, assignment, storeFields, gridColumns);
            }, this);
        }, this);
        return {
            storeStudents: storeStudents,
            storeFields: storeFields,
            gridColumns: gridColumns
        };
    },

    getStudentByName: function(username) {
        return this._students[username];
    },

    //getAssignmentById: function(id) {
        //return this._assignmentCollection.get(id);
    //},

    getAssignmentByShortName: function(short_name) {
        return this._assignmentCollection.findBy(function(assignmentrecord) {
            return assignmentrecord.data.short_name == short_name;
        }, this);
    },

    //validateAssignmentShortName: function(assignment_short_name) {
        //if(!this.getAssignmentByShortName(assignment_short_name)) {
            //throw Ext.String.format("{0}: Invalid assignment name: {1}", student.username, assignment_short_name);
        //}
    //}
});
