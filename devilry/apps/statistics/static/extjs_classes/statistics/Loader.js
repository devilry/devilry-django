Ext.define('devilry.statistics.Loader', {
    extend: 'Ext.util.Observable',
    requires: [
        'devilry.extjshelpers.AsyncActionPool'
    ],

    label_appkey: 'devilry.statistics.Labels',

    constructor: function(periodid, config) {

        this._students_by_releatedid = {};
        this._students = {};
        this.periodid = periodid;

        this.assignment_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
            remoteFilter: true,
            remoteSort: true
        });

        this.addEvents('loaded', 'datachange');
        // Copy configured listeners into *this* object so that the base class's
        // constructor will add them.
        this.listeners = config.listeners;

        this.callParent(arguments);        
        this._loadAllRelatedStudents(periodid);
    },

    /**
     * @private
     */
    _loadAllRelatedStudents: function() {
        var relatedstudent_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedRelatedStudent',
            remoteFilter: true,
            remoteSort: true
        });
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
        var relatedstudentkeyvalue_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedRelatedStudentKeyValue',
            remoteFilter: true,
            remoteSort: true
        });
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
            this._students_by_releatedid[relatedstudent_id].labels[label] = appKeyValueRecord;
        }, this);
        this._loadPeriod();
    },

    /**
     * @private
     */
    _loadPeriod: function() {
        Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedPeriod').load(this.periodid, {
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
        this.assignment_store.pageSize = 100000; // TODO: avoid UGLY hack
        this.assignment_store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: periodid
        }]);
        this.assignment_store.load({
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
            this._loadGroups(assignmentrecord.data.id, assignmentrecords.length);
        }, this);
    },

    /**
     * @private
     */
    _loadGroups: function(assignmentid, totalAssignments) {
        var assignmentgroup_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedAssignmentGroup',
            remoteFilter: true,
            remoteSort: true
        });
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
        //return this.assignment_store.findRecord('id', id);
    //},

    getAssignmentByShortName: function(short_name) {
        return this.assignment_store.findRecord('short_name', short_name);
    },

    //validateAssignmentShortName: function(assignment_id) {
        //if(!this.getAssignmentByShortName(assignment_id)) {
            //throw Ext.String.format("{0}: Invalid assignment name: {1}", student.username, assignment_id);
        //}
    //}

    setLabels: function(options) {
        var labelRecords = [];
        Ext.getBody().mask('Updating labels');
        var index = 0;
        this._finished = 0;
        this._watingFor = Ext.Object.getSize(this._students);
        Ext.Object.each(this._students, function(relstudentid, student) {
            var labelspec = Ext.bind(options.callback, options.scope)(student);
            var labelRecord = student.labels[labelspec.labelname];
            var has_label = labelRecord !== undefined; 
            if(labelspec.apply && !has_label) {
                this._createLabel(student, labelspec.labelname, index);
            } else if(!labelspec.apply && has_label) {
                this._deleteLabel(student, labelRecord, index);
            } else {
                this._checkFinished();
            }
            index ++;
        }, this);
    },

    _createLabel: function(student, labelname, index) {
        var record = this._createLabelRecord(student, labelname);
        devilry.extjshelpers.AsyncActionPool.add({
            scope: this,
            callback: function(pool) {
                record.save({
                    scope: this,
                    callback: function(records, op, successful) {
                        Ext.getBody().mask(Ext.String.format('Completed updating label {0}', index));
                        var label = record.get('key');
                        this._students[student.username].labels[label] = record;
                        pool.notifyTaskCompleted();
                        this._checkFinished();
                    }
                });
            }
        });
    },

    _deleteLabel: function(student, record, index) {
        devilry.extjshelpers.AsyncActionPool.add({
            scope: this,
            callback: function(pool) {
                record.destroy({
                    scope: this,
                    callback: function() {
                        Ext.getBody().mask(Ext.String.format('Completed updating label {0}', index));
                        var label = record.get('key');
                        this._students[student.username].labels[label] = undefined;
                        pool.notifyTaskCompleted();
                        this._checkFinished();
                    }
                });
            }
        });
    },

    _checkFinished: function(dontAddToFinished) {
        if(!dontAddToFinished) {
            this._finished ++;
        }
        if(this._watingFor == undefined) {
            return;
        }
        if(this._finished >= this._watingFor) {
            this._watingFor = undefined;
            Ext.getBody().unmask();
            this._onDataChanged();
        }
    },

    _createLabelRecord: function(student, labelname) {
        var record = Ext.create('devilry.apps.administrator.simplified.SimplifiedRelatedStudentKeyValue', {
            relatedstudent: student.relatedstudent.get('id'),
            application: this.label_appkey,
            key: labelname
        });
        return record;
    },

    _onDataChanged: function() {
        var extjsStructures = this.extjsFormat();
        this.fireEvent('datachange', extjsStructures);
    }
});
