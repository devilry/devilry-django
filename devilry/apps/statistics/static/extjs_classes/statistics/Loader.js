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

        this.addEvents('loaded', 'datachange', 'filterApplied', 'filterCleared');
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
        Ext.getBody().mask('Loading all students on the period', 'page-load-mask');
        relatedstudent_store.load({
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
        Ext.getBody().mask('Loading labels', 'page-load-mask');
        relatedstudentkeyvalue_store.load({
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
        Ext.getBody().mask('Loading detailed information about the Period', 'page-load-mask');
        Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedPeriod').load(this.periodid, {
            scope: this,
            callback: function(record, op) {
                if(!op.success) {
                    this._handleLoadError('Failed to load period', op);
                    return;
                }
                this.periodRecord = record;
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
        this._createModel();
        this._tmpAssignmentsWithAllGroupsLoaded = 0;
        Ext.getBody().mask('Loading all assignment groups (students) on all assignments within the period', 'page-load-mask');
        Ext.each(assignmentrecords, function(assignmentrecord, index) {
            this.assignment_ids.push(assignmentrecord.get('id'));
            this._loadGroups(assignmentrecord, assignmentrecords.length);
        }, this);
    },

    /**
     * @private
     */
    _loadGroups: function(assignmentrecord, totalAssignments) {
        var assignmentid = assignmentrecord.get('id');
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
            callback: function(grouprecords, op) {
                if(!op.success) {
                    this._handleLoadError('Failed to load assignment groups', op);
                    return;
                }
                Ext.getBody().mask(Ext.String.format('Finished loading all assignment groups (students) within: {0}', assignmentrecord.get('long_name')), 'page-load-mask');
                this._onLoadGroups(totalAssignments, grouprecords);
            }
        });
    },

    /**
     * @private
     */
    _onLoadGroups: function(totalAssignments, grouprecords) {
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
        var assignmentRecord = this.assignment_store.getById(grouprecord.data.parentnode);
        student.groupsByAssignmentId[grouprecord.data.parentnode] = {
            parentnode: grouprecord.get('parentnode'),
            points: grouprecord.data.feedback__points,
            is_passing_grade: grouprecord.data.feedback__is_passing_grade
        };
    },

    _onDataChanged: function() {
    },


    _createModel: function() {
        var fields = ['username', 'full_name', 'labels', 'student', 'relatedstudent', 'groupsByAssignmentId', 'totalScaledPoints'];
        Ext.each(this.assignment_store.data.items, function(assignmentRecord, index) {
            fields.push(assignmentRecord.get('short_name'));
            var scaledPointdataIndex = assignmentRecord.get('id') + '::scaledPoints';
            fields.push(scaledPointdataIndex);
        }, this);
        var model = Ext.define('devilry.statistics.AggregatedPeriodDataForStudentGenerated', {
            extend: 'devilry.statistics.AggregatedPeriodDataForStudentBase',
            fields: fields
        });
        return model;
    },

    _createStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: 'devilry.statistics.AggregatedPeriodDataForStudentGenerated',
            autoSync: false,
            proxy: 'memory'
        });
        Ext.Object.each(this._students, function(username, student, index) {
            var record = Ext.create('devilry.statistics.AggregatedPeriodDataForStudentBase', this.assignment_store, {
                username: username,
                full_name: student.relatedstudent.get('user__devilryuserprofile__full_name'),
                relatedstudent: student.relatedstudent,
                labelKeys: Ext.Object.getKeys(student.labels),
                groupsByAssignmentId: student.groupsByAssignmentId,
                labels: student.labels
            });
            store.add(record);
        }, this);
        return store;
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
