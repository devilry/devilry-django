Ext.define('devilry_qualifiesforexam.controller.QualifiesForExamShowStatusController', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_qualifiesforexam.controller.PeriodControllerMixin'
    ],

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
        'devilry_qualifiesforexam.utils.CreateStatus',
        'devilry_qualifiesforexam.utils.UrlLookup'
    ],


    refs: [{
        ref: 'overview',
        selector: 'showstatus'
    }, {
        ref: 'detailsGrid',
        selector: 'statusdetailsgrid'
    }, {
        ref: 'printLinkBox',
        selector: 'showstatus #printLinkBox'
    }, {
        ref: 'retractButton',
        selector: 'showstatus #retractButton'
    }, {
        ref: 'summary',
        selector: 'showstatus #summary'
    }],

    init: function() {
        this.control({
            'viewport showstatus statusdetailsgrid': {
                render: this._onRender
            },
            'viewport showstatus #retractButton': {
                click: this._onRetract
            },
            'viewport showstatus #updateButton': {
                click: this._onUpdate
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
        this.getOverview().setLoading();
        this.periodid = this.getOverview().periodid;
        this.loadPeriod(this.periodid);
    },

    getAppBreadcrumbs: function () {
        var text = gettext('Qualified for final exams');
        return [[], text];
    },

    onLoadPeriodSuccess: function () {
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
        if(this.statusRecord.getActiveStatus().status !== 'notready') {
            this.getRetractButton().show();
        }
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
        this.getOverview().setLoading(false);
    },

    _setupSummary:function () {
        var status = this.statusRecord.getActiveStatus();
        var qualifiedstudents = Ext.Object.getSize(status.passing_relatedstudentids_map);
        var totalstudents = this.detailedPeriodOverviewRecord.get('relatedstudents').length;
        var data = {
            loading: false,
            qualifiedstudents: qualifiedstudents,
            totalstudents: totalstudents,
            savetime: this.statusRecord.formatCreatetime(status.createtime),
            saveuser: Ext.String.format('<a href="mailto:{0}">{1}</a>',
                status.user.email, status.user.full_name)
        };
        Ext.apply(data, status);
        this.getSummary().update(data);
        if(status.status !== 'notready') {
            this.getPrintLinkBox().show();
            this.getPrintLinkBox().update({
                printstatusurl: devilry_qualifiesforexam.utils.UrlLookup.showstatus_print(status.id)
            });
        }
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
        if(!Ext.isEmpty(this.getOverview()) && this.getOverview().isVisible()) {
            this.getOverview().setLoading(false);
            var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
            errorhandler.addErrors(response, operation);
            if(errorhandler.errormessages.length === 1 && errorhandler.errormessages[0] === 'The period has no statuses') {
                this._onNoStatus();
            } else {
                this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
            }
        }
    },

    _onNoStatus:function () {
        this.application.route.navigate(devilry_qualifiesforexam.utils.UrlLookup.selectplugin(this.periodid));
    },

    _onRetract: function() {
        Ext.Msg.show({
            title: gettext('Why do you need to retract current status?'),
            msg: gettext('Explain why you need to change the status to "Not ready", and hit OK to save.'),
            scope: this,
            multiline: true,
            buttons: Ext.Msg.OKCANCEL,
            icon: Ext.Msg.QUESTION,
            width: 550,
            fn: function(btn, text){
                if(btn === 'ok'){
                    if(Ext.String.trim(text) === '') {
                        Ext.Msg.show({
                            title: gettext('Invalid input'),
                            msg: gettext('A message is required'),
                            buttons: Ext.Msg.OK,
                            icon: Ext.Msg.ERROR,
                            scope: this,
                            fn: function() {
                                this._onRetract();
                            }
                        });
                    } else {
                        this._retract(text);
                    }
                }
            }
        });
    },

    _retract: function (message) {
        devilry_qualifiesforexam.utils.CreateStatus.create({
            period: this.periodid,
            status: 'notready',
            message: message
        }, {
            scope: this,
            success:function () {
                window.location.reload();
            },
            failure: function (response) {
                devilry_qualifiesforexam.utils.CreateStatus.addErrorsToAlertmessagelist(
                    response,
                    this.application.getAlertmessagelist());
            }
        });
    },

    _onUpdate: function() {
        this.application.route.navigate(devilry_qualifiesforexam.utils.UrlLookup.selectplugin(this.periodid));
    }
});
