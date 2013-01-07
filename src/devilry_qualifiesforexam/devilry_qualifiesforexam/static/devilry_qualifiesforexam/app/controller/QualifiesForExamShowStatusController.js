Ext.define('devilry_qualifiesforexam.controller.QualifiesForExamShowStatusController', {
    extend: 'Ext.app.Controller',

    views: [
        'showstatus.QualifiesForExamShowStatus'
    ],

    stores: [
        'RelatedStudents'
    ],
    models: [
        'Status'
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
        console.log(this.statusRecord);
        var status = this.statusRecord.getActiveStatus();
        var passing_relatedstudentids_map = status.passing_relatedstudentids_map;
        console.log(passing_relatedstudentids_map);
        var grid = this.getDetailsGrid();
        grid.passing_relatedstudentids_map = passing_relatedstudentids_map;
//        previewGrid.addColumnForEachAssignment(perioddata.assignments);
//        previewGrid.addAssignmentSorters(perioddata.assignments);
//        previewGrid.sortByQualifiesQualifiedFirst();
//        this._loadRelatedStudentsIntoGridStore(perioddata.relatedstudents);
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

