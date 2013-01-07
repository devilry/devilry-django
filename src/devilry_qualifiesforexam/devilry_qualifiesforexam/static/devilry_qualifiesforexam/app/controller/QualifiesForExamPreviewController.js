Ext.define('devilry_qualifiesforexam.controller.QualifiesForExamPreviewController', {
    extend: 'Ext.app.Controller',

    views: [
        'preview.QualifiesForExamPreview'
    ],

    stores: [
        'RelatedStudents'
    ],

    models: [
        'Preview'
    ],

    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.HtmlErrorDialog'
    ],


    refs: [{
        ref: 'preview',
        selector: 'preview'
    }, {
        ref: 'previewGrid',
        selector: 'previewgrid'
    }],

    init: function() {
        this.control({
            'viewport preview previewgrid': {
                render: this._onRender
            },
            'viewport preview #saveButton': {
                click: this._onSave
            }
        });
        this.mon(this.getPreviewModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
    },

    _onRender: function() {
        this.periodid = this.getPreview().periodid;
        this.pluginsessionid = this.getPreview().pluginsessionid;
        this._loadPreviewModel();
    },

    _loadPreviewModel: function() {
        this.getPreviewModel().setParamsAndLoad(this.periodid, this.pluginsessionid, {
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onPreviewModelLoadSuccess(records);
                }
                // NOTE: Errors are handled in _onProxyError
            }
        });
    },

    _onPreviewModelLoadSuccess: function(record) {
        this.previewRecord = record;
        var perioddata = this.previewRecord.get('perioddata');
        var passing_relatedstudentids = this.previewRecord.get('pluginoutput').passing_relatedstudentids;
        var passing_relatedstudentids_map = Ext.Array.toMap(passing_relatedstudentids); // Turn into object for fast lookup
        var previewGrid = this.getPreviewGrid();
        previewGrid.passing_relatedstudentids_map = passing_relatedstudentids_map;
        previewGrid.addColumnForEachAssignment(perioddata.assignments);
        previewGrid.addAssignmentSorters(perioddata.assignments);
        previewGrid.sortByQualifiesQualifiedFirst();
        this._loadRelatedStudentsIntoGridStore(perioddata.relatedstudents);
    },

    _loadRelatedStudentsIntoGridStore: function(relatedstudents) {
        var relatedstudentsStore = this.getRelatedStudentsStore();
        relatedstudentsStore.loadData(relatedstudents);
    },

    _onProxyError: function(proxy, response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
    },


    _onSave:function () {
        var passing_relatedstudentids = this.previewRecord.get('pluginoutput').passing_relatedstudentids;
        Ext.Ajax.request({
            url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_qualifiesforexam/rest/status/',
            method: 'POST',
            jsonData: {
                period: this.periodid,
                status: 'ready',
                message: null,
                plugin: 'devilry_qualifiesforexam_approved.all',
                pluginsettings: null,
                passing_relatedstudentids: passing_relatedstudentids
            },
            extraParams: {
                format: 'json'
            },
            scope: this,
            success: this._onSaveSuccess(),
            failure: this._onSaveFailure()
        });
    },
    _onSaveSuccess:function (response) {
        console.log('Success');
    },
    _onSaveFailure:function (response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addRestErrorsFromResponse(response);
        this.application.getAlertmessagelist().addMany(
            errorhandler.asArrayOfStrings(), 'error', true);
    }
});

