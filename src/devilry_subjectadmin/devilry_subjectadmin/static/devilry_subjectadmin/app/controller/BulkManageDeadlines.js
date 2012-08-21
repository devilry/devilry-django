Ext.define('devilry_subjectadmin.controller.BulkManageDeadlines', {
    extend: 'Ext.app.Controller',

    requires: [
    ],

    views: [
        'bulkmanagedeadlines.BulkManageDeadlinesPanel'
    ],

    models: [
        //'BulkManageDeadlines',
    ],

    refs: [{
        ref: 'bulkManageDeadlinesPanel',
        selector: 'bulkmanagedeadlinespanel'
    }],

    init: function() {
        this.control({
            'viewport bulkmanagedeadlinespanel': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
        this.getBulkManageDeadlinesPanel().setLoading();
    }
});
