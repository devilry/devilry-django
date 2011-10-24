Ext.define('devilry.statistics.Loader', {
    extend: 'Ext.util.Observable',
    requires: [
        'devilry.extjshelpers.AsyncActionPool',
        'devilry.statistics.AggregatedPeriodDataForStudent',
        'devilry.statistics.AggregatedPeriodDataForStudentBase',
        'devilry.statistics.LabelManager'
    ],

    constructor: function(periodid, config) {
        this._students_by_releatedid = {};
        this.periodid = periodid;
        this.labelManager = Ext.create('devilry.statistics.LabelManager', {
            loader: this
            //listeners: {
                //scope: this,
                //changedMany: this._onDataChanged
            //}
        });

        this.assignment_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
            remoteFilter: true,
            remoteSort: true
        });
        this.assignment_ids = [];

        this.addEvents('loaded', 'datachange', 'filterApplied', 'filterCleared');
        // Copy configured listeners into *this* object so that the base class's
        // constructor will add them.
        this.listeners = config.listeners;

        this.callParent(arguments);        
        this._loadAssignments();
    },

    /**
     * @private
     */
    _loadAssignments: function() {
        this.assignment_store.pageSize = 100000; // TODO: avoid UGLY hack
        this.assignment_store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: this.periodid
        }]);
        Ext.getBody().mask('Loading all assignments within the period', 'page-load-mask');
        this.assignment_store.load({
            scope: this,
            callback: this._onAssignmentsLoaded
        });
    },

    /**
     * @private
     */
    _onAssignmentsLoaded: function(assignmentrecords, op) {
        if(!op.success) {
            this._handleLoadError('Failed to load assignments', op);
            return;
        }
        this._tmpAssignmentsWithAllGroupsLoaded = 0;
        Ext.getBody().mask('Loading all assignment groups (students) on all assignments within the period', 'page-load-mask');
        Ext.each(assignmentrecords, function(assignmentrecord, index) {
            this.assignment_ids.push(assignmentrecord.get('id'));
        }, this);
        this._loadAllRelatedStudents();
    },

    /**
     * @private
     */
    _loadAllRelatedStudents: function() {
        this.relatedstudent_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedRelatedStudent',
            remoteFilter: true,
            remoteSort: true
        });
        this.relatedstudent_store.pageSize = 100000; // TODO: avoid UGLY hack
        this.relatedstudent_store.proxy.setDevilryFilters([{
            field: 'period',
            comp: 'exact',
            value: this.periodid
        }]);
        Ext.getBody().mask('Loading all students on the period', 'page-load-mask');
        this.relatedstudent_store.load({
            scope: this,
            callback: this._onLoadAllRelatedStudents
        });
    },

    /**
     * @private
     */
    _onLoadAllRelatedStudents: function(records, op) {
        if(!op.success) {
            this._handleLoadError('Failed to load related students', op);
            return;
        }
        this._loadAllCandidatesInPeriod(this.periodid);
    },

    /** 
     * @private
     */
    _loadAllCandidatesInPeriod: function(periodid) {
        this.candidate_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedCandidate',
            remoteFilter: true,
            remoteSort: true
        });
        this.candidate_store.pageSize = 100000; // TODO: avoid UGLY hack
        this.candidate_store.proxy.setDevilryFilters([{
            field: 'assignment_group__parentnode__parentnode',
            comp: 'exact',
            value: this.periodid
        }]);
        Ext.getBody().mask('Loading all candidates on the period', 'page-load-mask');
        this.candidate_store.load({
            scope: this,
            callback: this._onLoadAllCandidatesInPeriod
        });
    },

    /**
     * @private
     */
    _onLoadAllCandidatesInPeriod: function(records, op) {
        if(!op.success) {
            this._handleLoadError('Failed to load candidates', op);
            return;
        }
        this._loadAllStudentLabels();
    },

    /**
     * @private
     */
    _loadAllStudentLabels: function() {
        this.relatedstudentkeyvalue_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedRelatedStudentKeyValue',
            remoteFilter: true,
            remoteSort: true
        });
        this.relatedstudentkeyvalue_store.pageSize = 100000; // TODO: avoid UGLY hack
        this.relatedstudentkeyvalue_store.proxy.setDevilryFilters([{
            field: 'relatedstudent__period',
            comp: 'exact',
            value: this.periodid
        }, {
            field: 'application',
            comp: 'exact',
            value: this.labelManager.application_id
        }]);
        Ext.getBody().mask('Loading labels', 'page-load-mask');
        this.relatedstudentkeyvalue_store.load({
            scope: this,
            callback: this._onLoadAllStudentLabels
        });
    },

    /**
     * @private
     */
    _onLoadAllStudentLabels: function(records, op) {
        if(!op.success) {
            this._handleLoadError('Failed to load labels', op);
            return;
        }
        this._loadPeriod();
    },

    /**
     * @private
     */
    _loadPeriod: function() {
        Ext.getBody().mask('Loading detailed information about the Period', 'page-load-mask');
        Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedPeriod').load(this.periodid, {
            scope: this,
            callback: function(record, op) {
                if(!op.success) {
                    this._handleLoadError('Failed to load period', op);
                    return;
                }
                this.periodRecord = record;
                this._loadAllGroupsInPeriod();
            }
        });
    },

    /**
     * @private
     */
    _loadAllGroupsInPeriod: function(assignmentrecord) {
        this.assignmentgroup_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedAssignmentGroup',
            remoteFilter: true,
            remoteSort: true
        });
        this.assignmentgroup_store.pageSize = 100000; // TODO: avoid UGLY hack
        this.assignmentgroup_store.proxy.setDevilryFilters([{
            field: 'parentnode__parentnode',
            comp: 'exact',
            value: this.periodid
        }]);
        Ext.getBody().mask('Loading all assignment groups in the Period', 'page-load-mask');
        this.assignmentgroup_store.load({
            scope: this,
            callback: this._onLoadAllGroupsInPeriod
        });
    },

    /**
     * @private
     */
    _onLoadAllGroupsInPeriod: function(grouprecords, op) {
        if(!op.success) {
            this._handleLoadError('Failed to load assignment groups', op);
            return;
        }
        this._onLoaded();
    },


    _addAllRelatedStudentsToStore: function() {
        Ext.each(this.relatedstudent_store.data.items, function(relatedStudentRecord, index) {
            var userid = relatedStudentRecord.get('user')
            var username = relatedStudentRecord.get('user__username')
            var record = Ext.create('devilry.statistics.AggregatedPeriodDataForStudentGenerated', {
                userid: userid,
                username: username,
                full_name: relatedStudentRecord.get('user__devilryuserprofile__full_name'),
                labelKeys: []
            });
            this.store.add(record);
            record.labels = [];
            record.assignment_store = this.assignment_store;
            record.relatedStudentRecord = relatedStudentRecord;
            record.groupsByAssignmentId = {};
            this._students_by_releatedid[relatedStudentRecord.get('id')] = record;
        }, this);
    },

    _addLabelsToStore: function() {
        Ext.each(this.relatedstudentkeyvalue_store.data.items, function(appKeyValueRecord, index) {
            var relatedstudent_id = appKeyValueRecord.get('relatedstudent');
            var label = appKeyValueRecord.get('key');
            var labelDescription = appKeyValueRecord.get('value');
            var studentRecord = this._students_by_releatedid[relatedstudent_id];
            studentRecord.labels[label] = appKeyValueRecord;
            studentRecord.setLabelKeysFromLabels();
        }, this);
    },

    _addAssignmentsToStore: function() {
        var assignment_ids = [];
        Ext.each(this.assignment_store.data.items, function(assignmentRecord, index) {
            assignment_ids.push(assignmentRecord.get('id'));
        }, this);
        Ext.each(this.store.data.items, function(studentRecord, index) {
            var groupsByAssignmentId = studentRecord.groupsByAssignmentId;
            Ext.each(this.assignment_store.data.items, function(assignmentRecord, index) {
                groupsByAssignmentId[assignmentRecord.get('id')] = {
                    candidates: [],
                    assignmentGroupRecord: null,
                    scaled_points: null
                };
            }, this);
            studentRecord.assignment_ids = assignment_ids;
        }, this);
    },

    _addGroupsToStore: function() {
        Ext.each(this.candidate_store.data.items, function(candidateRecord, index) {
            var student_id = candidateRecord.get('student');
            var studentRecord = this.store.getById(student_id);
            var assignmentgroup_id = candidateRecord.get('assignment_group');
            var assignmentGroupRecord = this.assignmentgroup_store.getById(assignmentgroup_id);

            var groupsByAssignmentId = studentRecord.groupsByAssignmentId;
            var assignment_id = assignmentGroupRecord.get('parentnode');
            var group = groupsByAssignmentId[assignment_id];
            group.candidates.push(candidateRecord); // This will add only unique candidate records, since we only fetch distinct candidates
            group.assignmentGroupRecord = assignmentGroupRecord; // This will be overwritten for each candidate, but that does not matter, since they overwrite with the same record
        }, this);
    },

    _mergeDataIntoStore: function() {
        this._addAllRelatedStudentsToStore();
        this._addLabelsToStore();
        this._addAssignmentsToStore();
        this._addGroupsToStore();
    },

    _onLoaded: function() {
        this._createStore();
        this.store.suspendEvents();
        this._mergeDataIntoStore();
        this.updateScaledPoints();
        this.store.resumeEvents();
        this.store.fireEvent('datachanged');
        this.fireEvent('loaded', this);
    },

    /**
     * @private
     */
    //_addGroupToStudent: function(username, grouprecord) {
        //if(!this._students[username]) {
            ////console.error(Ext.String.format('Skipped {0} because the user is not a related student.', username));
            //return;
        //}
        //var student = this._students[username];
        //var assignmentRecord = this.assignment_store.getById(grouprecord.data.parentnode);
        //student.groupsByAssignmentId[grouprecord.data.parentnode] = {
            //parentnode: grouprecord.get('parentnode'),
            //points: grouprecord.data.feedback__points,
            //is_passing_grade: grouprecord.data.feedback__is_passing_grade
        //};
    //},

    //_onDataChanged: function() {
    //},


    _createModel: function() {
        var fields = ['userid', 'username', 'full_name', 'labelKeys', 'student', 'totalScaledPoints'];
        Ext.each(this.assignment_store.data.items, function(assignmentRecord, index) {
            fields.push(assignmentRecord.get('short_name'));
            var scaledPointdataIndex = assignmentRecord.get('id') + '::scaledPoints';
            fields.push(scaledPointdataIndex);
        }, this);
        var model = Ext.define('devilry.statistics.AggregatedPeriodDataForStudentGenerated', {
            extend: 'devilry.statistics.AggregatedPeriodDataForStudentBase',
            idProperty: 'userid',
            fields: fields
        });
    },

    _createStore: function() {
        this._createModel();
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.statistics.AggregatedPeriodDataForStudentGenerated',
            autoSync: false,
            proxy: 'memory'
        });

        //Ext.Object.each(this._students, function(username, student, index) {
            //var record = Ext.create('devilry.statistics.AggregatedPeriodDataForStudentBase', this.assignment_store, {
                //username: username,
                //full_name: student.relatedstudent.get('user__devilryuserprofile__full_name'),
                //relatedstudent: student.relatedstudent,
                //labelKeys: Ext.Object.getKeys(student.labels),
                //groupsByAssignmentId: student.groupsByAssignmentId,
                //labels: student.labels
            //});
            //store.add(record);
        //}, this);
        //return store;
    },

    updateScaledPoints: function() {
        this.store.suspendEvents(); // without suspendEvents/resumeEvents, each record change fires an update event, which makes updateScaledPoints take forever for huge datasets.
        Ext.each(this.store.data.items, function(studentRecord, index) {
            studentRecord.updateScaledPoints();
        }, this);
        this.store.resumeEvents();
        this.store.fireEvent('datachanged');
    },

    filterBy: function(description, fn, scope) {
        this.store.filterBy(fn, scope);
        this.fireEvent('filterApplied', this, description);
    },

    clearFilter: function() {
        this.store.clearFilter();
        this.fireEvent('filterCleared', this);
    },

    _handleLoadError: function(details, op) {
        Ext.getBody().unmask();
        var httperror = 'Lost connection with server';
        if(op.error.status !== 0) {
            httperror = Ext.String.format('{0} {1}', op.error.status, op.error.statusText);
        }
        Ext.MessageBox.show({
            title: 'Failed to load the period overview',
            msg: '<p>This is usually caused by an unstable server connection. <strong>Try reloading the page</strong>.</p>' +
                Ext.String.format('<p>Error details: {0}: {1}</p>', httperror, details),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    }
});
