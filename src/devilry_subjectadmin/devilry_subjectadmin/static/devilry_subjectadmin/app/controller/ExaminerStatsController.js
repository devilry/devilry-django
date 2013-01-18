Ext.define('devilry_subjectadmin.controller.ExaminerStatsController', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin',
        'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    requires: [
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler'
    ],

    views: [
        'examinerstats.ExaminerStatsOverview'
    ],

    models: [
        'Assignment'
    ],

    stores: [
    ],

    refs: [{
        ref: 'overview',
        selector: 'examinerstatsoverview'
    }, {
        ref: 'globalAlertmessagelist',
        selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
    }],

    init: function() {
        this.control({
            'viewport examinerstatsoverview': {
                render: this._onRender
            }
        });

//        this.mon(this.getDeadlinesBulkStore().proxy, {
//            scope: this,
//            exception: this._onDeadlinesBulkStoreProxyError
//        });
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        this.getOverview().setLoading();
        this.assignment_id = this.getOverview().assignment_id;
        this.loadAssignment(this.assignment_id);
//        var store = this.getDeadlinesBulkStore();
//        store.proxy.setUrl(this.assignment_id);
//        store.load({
//            scope: this,
//            callback: function(records, operation) {
//                this.getBulkManageDeadlinesPanel().setLoading(false);
//                if(operation.success) {
//                    this._onLoadSuccess(records, operation);
//                } else {
//                    NOTE: Failure is handled in _onDeadlinesBulkStoreProxyError()
//                }
//            }
//        });
    },

    _setBreadcrumbAndTitle: function(subviewtext) {
        var text = gettext('Examiner statistics');
        this.setSubviewBreadcrumb(this.assignmentRecord, 'Assignment', [], text);
        var path = this.getPathFromBreadcrumb(this.assignmentRecord);
        this.application.setTitle(Ext.String.format('{0}.{1}', path, text));
    },
    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        this._setBreadcrumbAndTitle();
    },
    onLoadAssignmentFailure: function(operation) {
        this.onLoadFailure(operation);
    },

    _onLoadSuccess: function(deadlineRecords, operation) {
    },

    _scrollTo: function(component) {
        component.el.scrollIntoView(this.getOverview().getEl(), false, true);
    }
});
