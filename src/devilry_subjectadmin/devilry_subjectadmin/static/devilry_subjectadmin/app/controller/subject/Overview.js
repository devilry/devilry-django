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

    _onSubjectViewRender: function() {
        this.subject_shortname = this.getSubjectOverview().subject_shortname;
        this._loadSubject();
        this._loadPeriods();
    },

    _loadSubject: function() {
        this.getSubjectsStore().loadSubject(
            this.subject_shortname, this._onLoadSubject, this
        );
    },

    _onLoadSubject: function(records, operation) {
        if(operation.success) {
            this._onLoadSubjectSuccess(records[0]);
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
    },

    _loadPeriods: function() {
        this.getPeriodsStore().loadPeriodsInSubject(this.subject_shortname, this._onLoadPeriods, this);
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
