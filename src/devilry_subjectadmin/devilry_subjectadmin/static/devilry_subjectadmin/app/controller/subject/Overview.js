/**
 * Controller for the subject overview.
 */
Ext.define('devilry_subjectadmin.controller.subject.Overview', {
    extend: 'Ext.app.Controller',

    views: [
        'subject.Overview',
        'subject.ListOfPeriods',
        'ActionList'
    ],

    stores: [
        'Subjects',
        'Periods'
    ],
    
    models: ['Subject'],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'subjectoverview>alertmessagelist'
    }, {
        ref: 'actions',
        selector: 'subjectoverview #actions'
    }, {
        ref: 'subjectOverview',
        selector: 'subjectoverview'
    }],

    init: function() {
        this.control({
            'viewport subjectoverview': {
                render: this._onSubjectViewRender
            },
            'viewport subjectoverview editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            }
        });
    },

    _setBreadcrumbs: function(breadcrumbsExtra, current) {
        var breadcrumbsBase = [{
            text: gettext("All subjects"),
            url: '/'
        }];
        var breadcrumbs = breadcrumbsBase.concat(breadcrumbsExtra);
        this.application.breadcrumbs.set(breadcrumbs, current);
    },

    _onSubjectViewRender: function() {
        this._setBreadcrumbs([], gettext('Loading ...'));
        this.subject_id = this.getSubjectOverview().subject_id;
        this._loadSubject();
        this._loadPeriods();
    },

    _loadSubject: function() {
        //this.getSubjectsStore().loadSubject(
            //this.subject_id, this._onLoadSubject, this
        //);
        this.getSubjectModel().load(this.subject_id, {
            callback: this._onLoadSubject,
            scope: this
        });
    },

    _onLoadSubject: function(record, operation) {
        if(operation.success) {
            this._onLoadSubjectSuccess(record);
        } else {
            this._onLoadSubjectFailure(operation);
        }
    },

    _onLoadSubjectFailure: function(operation) {
        var error = Ext.create('devilry_extjsextras.RestfulApiProxyErrorHandler', operation);
        error.addErrors(operation);
        this.getGlobalAlertmessagelist().addMany(error.errormessages, 'error');
    },

    _onLoadSubjectSuccess: function(record) {
        this.assignmentRecord = record;
        this.getActions().setTitle(record.get('long_name'));
        this._setBreadcrumbs([], record.get('short_name'));
    },

    _loadPeriods: function() {
        this.getPeriodsStore().loadPeriodsInSubject(this.subject_id, this._onLoadPeriods, this);
    },

    _onLoadPeriods: function(records, operation) {
        if(operation.success) {
            
        } else {
            var error = Ext.create('devilry_extjsextras.RestfulApiProxyErrorHandler', operation);
            error.addErrors(operation);
            this.getGlobalAlertmessagelist().addMany(error.errormessages, 'error');
        }
    }
});
