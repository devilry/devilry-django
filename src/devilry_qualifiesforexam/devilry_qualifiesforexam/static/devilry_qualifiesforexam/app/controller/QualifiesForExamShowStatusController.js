Ext.define('devilry_qualifiesforexam.controller.QualifiesForExamShowStatusController', {
    extend: 'Ext.app.Controller',

    views: [
        'showstatus.QualifiesForExamShowStatus'
    ],

    stores: [
        'RelatedStudents'
    ],
    models: [
        'Status',
        'DetailedPeriodOverview'
    ],

    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.HtmlErrorDialog'
    ],


    refs: [{
        ref: 'overview',
        selector: 'showstatus'
    }, {
        ref: 'detailsGrid',
        selector: 'statusdetailsgrid'
    }, {
        ref: 'summary',
        selector: 'showstatus #summary'
    }],

    init: function() {
        this.control({
            'viewport showstatus statusdetailsgrid': {
                render: this._onRender
            }
        });
        this.mon(this.getStatusModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
        this.mon(this.getDetailedPeriodOverviewModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
    },

    _onRender: function() {
        this.periodid = this.getOverview().periodid;
        this._loadStatusModel();
    },

    _loadStatusModel: function() {
        this.getStatusModel().load(this.periodid, {
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onStatusModelLoadSuccess(records);
                }
                // NOTE: Errors are handled in _onProxyError
            }
        });
    },

    _onStatusModelLoadSuccess: function(record) {
        this.statusRecord = record;
        this._loadDetailedPeriodOverview();
    },

    _loadDetailedPeriodOverview: function() {
        this.getDetailedPeriodOverviewModel().load(this.periodid, {
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadDetailedPeriodOverviewSuccess(records);
                }
                // NOTE: Errors are handled in _onProxyError
            }
        });
    },
    _onLoadDetailedPeriodOverviewSuccess: function(record) {
        this.detailedPeriodOverviewRecord = record;
        this._onLoadAllComplete();
    },

    _onLoadAllComplete: function() {
        this._setupSummary();
        this._setupGrid();
    },

    _setupSummary:function () {
        var status = this.statusRecord.getActiveStatus();
        var qualifiedstudents = Ext.Object.getSize(status.passing_relatedstudentids_map);
        var totalstudents = this.detailedPeriodOverviewRecord.get('relatedstudents').length;
        var data = {
            loading: false,
            qualifiedstudents: qualifiedstudents,
            totalstudents: totalstudents
        };
        Ext.apply(data, status);
        this.getSummary().update(data);
    },

    _setupGrid:function () {
        var status = this.statusRecord.getActiveStatus();
        var passing_relatedstudentids_map = status.passing_relatedstudentids_map;
        var grid = this.getDetailsGrid();
        grid.passing_relatedstudentids_map = passing_relatedstudentids_map;
        var assignments = this.detailedPeriodOverviewRecord.get('assignments');
        grid.addColumnForEachAssignment(assignments);
        grid.addAssignmentSorters(assignments);
        grid.sortByQualifiesQualifiedFirst();
        this._loadRelatedStudentsIntoGridStore(this.detailedPeriodOverviewRecord.get('relatedstudents'));
    },

    _loadRelatedStudentsIntoGridStore: function(relatedstudents) {
        var relatedstudentsStore = this.getRelatedStudentsStore();
        relatedstudentsStore.loadData(relatedstudents);
    },

    _onProxyError: function(proxy, response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
    }
});

