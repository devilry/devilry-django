Ext.define('devilry_qualifiesforexam.controller.QualifiesForExamPreviewController', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_qualifiesforexam.controller.PeriodControllerMixin'
    ],

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
        'devilry_qualifiesforexam.utils.CreateStatus',
        'devilry_qualifiesforexam.utils.UrlLookup'
    ],


    refs: [{
        ref: 'preview',
        selector: 'preview'
    }, {
        ref: 'previewGrid',
        selector: 'preview previewgrid'
    }],

    init: function() {
        this.control({
            'viewport preview previewgrid': {
                render: this._onRender
            },
            'viewport preview #saveButton': {
                click: this._onSave
            },
            'viewport preview #backButton': {
                click: this._onBack
            }
        });
        this.mon(this.getPreviewModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
    },

    _onRender: function() {
        this.getPreview().setLoading();
        this.periodid = this.getPreview().periodid;
        this.pluginid = this.getPreview().pluginid;
        this.pluginsessionid = this.getPreview().pluginsessionid;
        this.application.setTitle(gettext('Preview and confirm'));
        this.loadPeriod(this.periodid);
    },

    getAppBreadcrumbs: function () {
        var text = gettext('Qualified for final exams') + ' - ' + gettext('preview');
        return [[], text];
    },

    onLoadPeriodSuccess: function () {
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
        this.getPreview().setLoading(false);
    },

    _loadRelatedStudentsIntoGridStore: function(relatedstudents) {
        var relatedstudentsStore = this.getRelatedStudentsStore();
        relatedstudentsStore.loadData(relatedstudents);
    },

    _onProxyError: function(proxy, response, operation) {
        this.getPreview().setLoading(false);
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
    },


    _onSave:function () {
        var passing_relatedstudentids = this.previewRecord.get('pluginoutput').passing_relatedstudentids;
        devilry_qualifiesforexam.utils.CreateStatus.create({
            period: this.periodid,
            status: 'ready',
            message: null,
            plugin: this.pluginid,
            pluginsessionid: this.pluginsessionid,
            passing_relatedstudentids: passing_relatedstudentids
        }, {
            scope: this,
            success: this._onSaveSuccess,
            failure: function (response) {
                devilry_qualifiesforexam.utils.CreateStatus.addErrorsToAlertmessagelist(
                    response,
                    this.application.getAlertmessagelist());
            }
        });
    },
    _onSaveSuccess:function (response) {
        this.application.route.navigate(
            devilry_qualifiesforexam.utils.UrlLookup.showstatus(this.periodid));
    },

    _onBack:function () {
        if(Ext.isIE) {
            window.history.go(-2);
        } else {
            window.history.go(-3);
        }
    }
});

