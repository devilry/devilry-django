/**
 * Controller for the related students view
 */
Ext.define('devilry_subjectadmin.controller.RelatedStudents', {
    extend: 'Ext.app.Controller',

    mixins: {
        'setBreadcrumb': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'onLoadFailure': 'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin'
    },

    views: [
        'relatedstudents.Overview'
    ],

    stores: ['RelatedStudents'],
    models: ['Period'],

    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'viewport relatedstudents>alertmessagelist'
    }, {
        ref: 'overview',
        selector: 'viewport relatedstudents'
    }],

    init: function() {
        this.control({
            'viewport relatedstudents': {
                render: this._onRender
            },
            'viewport relatedstudents #addButton': {
                click: this._onAdd
            }
        });
    },

    _loadRelatedUsers: function(period_id) {
        this.getRelatedStudentsStore().loadInPeriod(period_id, {
            scope: this,
            callback: this._onLoadRelatedStudents
        });
    },

    _onLoadRelatedStudents: function(records, operation) {
        if(operation.success) {
            this._onLoadRelatedStudentsSuccess(records);
        } else {
            this._onLoadRelatedStudentsFailure(operation);
        }
    },
    _onLoadRelatedStudentsSuccess: function(records) {
        console.log(records);
    },
    _onLoadRelatedStudentsFailure: function(operation) {
        this.onLoadFailure(operation);
    },


    _onRender: function() {
        this.setLoadingBreadcrumb();
        this.period_id = this.getOverview().period_id;
        this._loadPeriod(this.period_id);
        this._loadRelatedUsers(this.period_id);
    },

    _getPath: function() {
        return 
    },

    _loadPeriod: function(period_id) {
        this.getPeriodModel().load(period_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this._onLoadPeriodSuccess(record);
                } else {
                    this._onLoadPeriodFailure(operation);
                }
            }
        });
    },
    _onLoadPeriodSuccess: function(record) {
        this.periodRecord = record;
        var path = this.getPathFromBreadcrumb(this.periodRecord);
        var label = gettext('Manage students');
        this.application.setTitle(Ext.String.format('{0} - {1}', label, path));
        this.setSubviewBreadcrumb(this.periodRecord, 'Period', [], label);
    },
    _onLoadPeriodFailure: function(operation) {
        this.onLoadFailure(operation);
    },

    _onAdd: function() {
        console.log('ADD');
    }
});
