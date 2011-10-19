Ext.define('devilry.statistics.Loader', {
    extend: 'Ext.util.Observable',

    label_appkey: 'devilry.statistics',

    constructor: function(periodid, config) {
        this._students_by_releatedid = {};
        this._students = {};
        this._assignmentCollection = Ext.create('Ext.util.MixedCollection');
        this.periodid = periodid;
        this._loadAllRelatedStudents(periodid);

        this.addEvents('loaded');

        // Copy configured listeners into *this* object so that the base class's
        // constructor will add them.
        this.listeners = config.listeners;

        this.callParent(arguments);        
    },

    /**
     * @private
     */
    _loadAllRelatedStudents: function() {
        relatedstudent_store.pageSize = 100000; // TODO: avoid UGLY hack
        relatedstudent_store.proxy.setDevilryFilters([{
            field: 'period',
            comp: 'exact',
            value: this.periodid
        }]);
        relatedstudent_store.load({
            scope: this,
            callback: this._onLoadAllRelatedStudents
        });
    },

    /**
     * @private
     */
    _onLoadAllRelatedStudents: function(records, success) {
        // TODO: Handle errors
        Ext.each(records, function(relatedStudentRecord, index) {
            var username = relatedStudentRecord.get('user__username')
            this._students[username] = {
                username: username,
                relatedstudent: relatedStudentRecord,
                labels: {},
                groupsByAssignmentId: {}
            };
            this._students_by_releatedid[relatedStudentRecord.get('id')] = this._students[username];
        }, this);
        this._loadAllStudentLabels();
    },

    /**
     * @private
     */
    _loadAllStudentLabels: function() {
        relatedstudentkeyvalue_store.pageSize = 100000; // TODO: avoid UGLY hack
        relatedstudentkeyvalue_store.proxy.setDevilryFilters([{
            field: 'relatedstudent__period',
            comp: 'exact',
            value: this.periodid
        }, {
            field: 'application',
            comp: 'exact',
            value: this.label_appkey
        }]);
        relatedstudentkeyvalue_store.load({
            scope: this,
            callback: this._onLoadAllStudentLabels
        });
    },

    /**
     * @private
     */
    _onLoadAllStudentLabels: function(records, success) {
        // TODO: Handle errors
        Ext.each(records, function(appKeyValueRecord, index) {
            var relatedstudent_id = appKeyValueRecord.get('relatedstudent');
            var label = appKeyValueRecord.get('key');
            var labelDescription = appKeyValueRecord.get('value');
            this._students_by_releatedid[relatedstudent_id].labels[label] = labelDescription;
        }, this);
        this._loadPeriod();
    },

    /**
     * @private
     */
    _loadPeriod: function() {
        period_model.load(this.periodid, {
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
        assignment_store.pageSize = 100000; // TODO: avoid UGLY hack
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
        assignmentgroup_store.pageSize = 100000; // TODO: avoid UGLY hack
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
            console.error(Ext.String.format('Skipped {0} because the user is not a related student.', username));
            return;
        }
        var student = this._students[username];
        student.groupsByAssignmentId[grouprecord.data.parentnode] = {
            assignment_shortname: grouprecord.data.parentnode__short_name,
            points: grouprecord.data.feedback__points,
            scaled_points: grouprecord.data.feedback__points,
            is_passing_grade: grouprecord.data.feedback__is_passing_grade
        };
    },


    /**
     * @private
     */
    _extjsFormatSingleAssignment: function(studentStoreFmt, assignment_id, group, storeFields, gridColumns) {
        var pointdataIndex = assignment_id + '::points';
        var scaledPointdataIndex = assignment_id + '::scaledPoints';
        var passingdataIndex = assignment_id + '::is_passing_grade';
        studentStoreFmt[pointdataIndex] = group.points;
        studentStoreFmt[scaledPointdataIndex] = group.scaled_points;
        studentStoreFmt[passingdataIndex] = group.is_passing_grade;

        if(!Ext.Array.contains(storeFields, pointdataIndex)) {
            storeFields.push(pointdataIndex);
            storeFields.push(scaledPointdataIndex);
            storeFields.push(passingdataIndex);
            gridColumns.push({
                //text: group.assignment_shortname,
                text: Ext.String.format('{0} (id: {1})', group.assignment_shortname, assignment_id),
                columns: [{
                    dataIndex: scaledPointdataIndex,
                    text: 'Scaled points',
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
        var storeFields = ['username', 'labels'];
        var pointsTpl = Ext.create('Ext.XTemplate',
            '<ul class="labels-list">',
            '    <tpl for="labels">',
            '       <li class="label-{.}">{.}</li>',
            '    </tpl>',
            '</ul>'
        );
        var gridColumns = [{
            header: 'Username', dataIndex: 'username'
        }, {
            header: 'Labels', dataIndex: 'labels',
            renderer: function(value, p, record) {
                return pointsTpl.apply(record.data);
            }
        }];
        Ext.Object.each(this._students, function(username, student, index) {
            var studentStoreFmt = {username: username};
            storeStudents.push(studentStoreFmt);
            Ext.Object.each(student.groupsByAssignmentId, function(assignment_id, group, index) {
                this._extjsFormatSingleAssignment(studentStoreFmt, assignment_id, group, storeFields, gridColumns);
            }, this);

            studentStoreFmt['labels'] = Ext.Object.getKeys(student.labels);
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
    }

    //validateAssignmentShortName: function(assignment_id) {
        //if(!this.getAssignmentByShortName(assignment_id)) {
            //throw Ext.String.format("{0}: Invalid assignment name: {1}", student.username, assignment_id);
        //}
    //}
});
