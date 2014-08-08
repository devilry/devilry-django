Ext.define('devilry_subjectadmin.controller.Dashboard', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'dashboard.Dashboard'
    ],

    stores: [
        'AllActivesWhereIsAdmin'
    ],

    refs: [{
        ref: 'allWhereIsAdminList',
        selector: 'allactivewhereisadminlist'
    }],

    init: function() {
        this.control({
            'viewport dashboard allactivewhereisadminlist': {
                render: this._onRenderAllWhereIsAdminList
            }
        });
        this.mon(this.getAllActivesWhereIsAdminStore().proxy, {
            scope: this,
            exception: this._onProxyError
        });
    },

    _onRenderAllWhereIsAdminList: function() {
        this.getAllActivesWhereIsAdminStore().load({
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadSuccess(records);
                } else {
                    // NOTE: Errors are handled in _onProxyError
                }
            }
        });
    },

    _flattenListOfActive: function(records) {
        var list = [];
        Ext.Array.each(records, function(record) {
            var subject = record.data;
            var multipleActivePeriods = subject.periods.length > 1;
            Ext.Array.each(subject.periods, function(period) {
                if(period.can_administer) {
                    list.push({
                        text: subject.long_name,
                        //suffix: multipleActivePeriods? period.long_name: null,
                        suffix: period.long_name,
                        type: 'period',
                        id: period.id
                    });
                } else {
                    Ext.Array.each(period.assignments, function(assignment) {
                        list.push({
                            text: Ext.String.format('{0} - {1}',
                                subject.short_name, assignment.long_name),
                                suffix: period.long_name,
                                //suffix: multipleActivePeriods? period.long_name: null,
                            type: 'assignment',
                            id: assignment.id
                        });
                    }, this);
                }
            }, this);
        }, this);
        return list;
    },

    _onLoadSuccess: function(records) {
        this.getAllWhereIsAdminList().update({
            loadingtext: null,
            list: this._flattenListOfActive(records)
        });
    },

    _onProxyError: function(proxy, response, operation) {
        this.handleProxyErrorNoForm(this.application.getAlertmessagelist(),
            response, operation);
    }
});

