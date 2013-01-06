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
            'viewport previewgrid': {
                render: this._onRender
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
        this._addColumnForEachAssignment(perioddata.assignments);
        this._loadRelatedStudentsIntoGridStore(perioddata.relatedstudents);
    },

    _addColumnForEachAssignment:function (assignments) {
        var grid = this.getPreviewGrid();
        Ext.Array.each(assignments, function(assignment) {
            grid.addAssignmentResultColumn(assignment);
        }, this);
        grid.getView().refresh();
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

