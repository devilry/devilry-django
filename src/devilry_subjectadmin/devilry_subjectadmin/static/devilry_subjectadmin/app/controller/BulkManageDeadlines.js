Ext.define('devilry_subjectadmin.controller.BulkManageDeadlines', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin'
    ],

    views: [
        'bulkmanagedeadlines.BulkManageDeadlinesPanel'
    ],

    models: [
        //'DeadlineBulk'
    ],
    stores: [
        'DeadlinesBulk'
    ],

    refs: [{
        ref: 'bulkManageDeadlinesPanel',
        selector: 'bulkmanagedeadlinespanel'
    }, {
        ref: 'globalAlertmessagelist',
        selector: 'bulkmanagedeadlinespanel alertmessagelist'
    }],

    init: function() {
        this.control({
            'viewport bulkmanagedeadlinespanel alertmessagelist': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
        this.getBulkManageDeadlinesPanel().setLoading();
        var assignment_id = this.getBulkManageDeadlinesPanel().assignment_id;
        var store = this.getDeadlinesBulkStore();
        store.proxy.setUrl(assignment_id);
        store.load({
            scope: this,
            callback: function(records, operation) {
                this.getBulkManageDeadlinesPanel().setLoading(false);
                if(operation.success) {
                    this._onLoadSuccess(records, operation);
                } else {
                    this.onLoadFailure(operation);
                }
            }
        });
    },

    _onLoadSuccess: function(records, operation) {
        console.log('Loaded', records);
    }
});
