Ext.define('devilry.statistics.Loader', {
    extend: 'Ext.util.Observable',
    requires: [
        'devilry.extjshelpers.AsyncActionPool',
        'devilry.statistics.AggregatedPeriodDataForStudent',
        'devilry.statistics.LabelManager'
    ],

    constructor: function(periodid, config) {

        this._students_by_releatedid = {};
        this._students = {};
        this.periodid = periodid;
        this.labelManager = Ext.create('devilry.statistics.LabelManager', {
            loader: this,
            listeners: {
                scope: this,
                changedMany: this._onDataChanged
            }
        });

        this.assignment_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
            remoteFilter: true,
            remoteSort: true
        });
        this.assignment_ids = [];

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
            this._students[username] = Ext.create('devilry.statistics.AggregatedPeriodDataForStudent', {
                username: username,
                relatedstudent: relatedStudentRecord
            });
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
            value: this.labelManager.application_id
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
            this.assignment_ids.push(assignmentrecord.get('id'));
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
                this._addGroupToStudent(username, grouprecord);
            }, this);
        }, this);

        this._tmpAssignmentsWithAllGroupsLoaded ++;
        if(this._tmpAssignmentsWithAllGroupsLoaded == totalAssignments) {
            this.store = this._createStore();
            this.fireEvent('loaded', this);
        }
    },

    /**
     * @private
     */
    _addGroupToStudent: function(username, grouprecord) {
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

    _onDataChanged: function() {
        //var extjsStructures = this.dataView.refresh();
        this.fireEvent('datachange');
    },


    calculateScaledPoints: function(group) {
        return group.points;
    },


    _createModel: function() {
        var fields = ['username', 'labels', 'student'];
        Ext.each(this.assignment_store.data.items, function(assignmentRecord, index) {
            fields.push(assignmentRecord.get('short_name'));
            var scaledPointdataIndex = assignmentRecord.get('id') + '::scaledPoints';
            fields.push(scaledPointdataIndex);
        }, this);
        var model =Ext.define('devilry.statistics.AggregatedPeriodDataForStudent', {
            extend: 'Ext.data.Model',
            fields: fields
        });
        return model;
    },

    _createStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: this._createModel(),
            proxy: 'memory'
        });
        Ext.Object.each(this._students, function(username, student, index) {
            var studentStoreFmt = {
                username: username,
                student: student,
                labels: Ext.Object.getKeys(student.labels)
            };
            Ext.Object.each(student.groupsByAssignmentId, function(assignment_id, group, index) {
                studentStoreFmt[assignment_id] = group;
                var scaledPointdataIndex = assignment_id + '::scaledPoints';
                studentStoreFmt[scaledPointdataIndex] = this.calculateScaledPoints(group);
            }, this);
            store.add(studentStoreFmt);
        }, this);
        return store;
    }
});
