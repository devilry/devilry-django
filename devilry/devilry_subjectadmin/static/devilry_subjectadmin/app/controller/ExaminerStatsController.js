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
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_subjectadmin.view.examinerstats.SingleExaminerStatBox',
        'Ext.util.Sorter'
    ],

    views: [
        'examinerstats.ExaminerStatsOverview'
    ],

    models: [
        'Assignment'
    ],

    stores: [
        'ExaminerStats'
    ],

    refs: [{
        ref: 'overview',
        selector: 'examinerstatsoverview'
    }, {
        ref: 'examinerStatBoxes',
        selector: 'examinerstatsoverview #examinerStatBoxes'
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
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        this.getOverview().setLoading();
        this.assignment_id = this.getOverview().assignment_id;
        this.loadAssignment(this.assignment_id);
        this._loadExaminerStats();
    },

    _setBreadcrumbAndTitle: function(subviewtext) {
        var text = gettext('Statistics about examiners');
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


    _loadExaminerStats:function () {
        var store = this.getExaminerStatsStore();
        store.proxy.setUrl(this.assignment_id);
        store.load({
            scope: this,
            callback: function(records, operation) {
                this.getOverview().setLoading(false);
                if(operation.success) {
                    this._onLoadExaminerStatsSuccess(records, operation);
                } else {
                    this.onLoadFailure(operation);
                }
            }
        });
    },

    _onLoadExaminerStatsSuccess: function(records, operation) {
        var examinerStatBoxes = this.getExaminerStatBoxes();
        var store = this.getExaminerStatsStore();
        store.sort(Ext.create('Ext.util.Sorter', {
            sorterFn: function (a, b) {
                return a.get('examiner').user.displayname.localeCompare(
                    b.get('examiner').user.displayname);
            }
        }));
        store.each(function (record, index) {
            var margin = '20 0 0 0';
            if(index === 0) {
                margin = '0';
            }
            examinerStatBoxes.add({
                xtype: 'singleexaminerstatbox',
                examinerstat: record,
                margin: margin
            });
        });
    },

    _scrollTo: function(component) {
        component.el.scrollIntoView(this.getOverview().getEl(), false, true);
    }
});
