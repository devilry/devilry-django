Ext.define('devilry_student.controller.GroupInfo', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.window.MessageBox'
    ],

    views: [
        'groupinfo.Overview',
        'groupinfo.DeadlinePanel',
        'groupinfo.DeliveryPanel'
    ],

    models: ['GroupInfo'],

    refs: [{
        ref: 'overview',
        selector: 'viewport groupinfo'
    }, {
        ref: 'deadlinesContainer',
        selector: 'viewport groupinfo #deadlinesContainer'
    }],

    init: function() {
        this.control({
            'viewport groupinfo #deadlinesContainer': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
        var group_id = this.getOverview().group_id;
        this.getGroupInfoModel().load(group_id, {
            scope: this,
            success: this._onGroupInfoLoadSuccess,
            failure: this._onGroupInfoLoadFailure
        });
    },

    _onGroupInfoLoadSuccess: function(groupInfoRecord) {
        this._populateDeadlinesContainer(groupInfoRecord.get('deadlines'), groupInfoRecord.get('active_feedback'));
    },

    _onGroupInfoLoadFailure: function() {
        Ext.MessageBox.alert(gettext('Error'),
            gettext('Failed to load group. Try to reload the page'));
    },

    _addDeadlineToContainer: function(deadline, active_feedback) {
        this.getDeadlinesContainer().add({
            xtype: 'groupinfo_deadline',
            deadline: deadline,
            active_feedback: active_feedback
        });
    },

    _populateDeadlinesContainer: function(deadlines, active_feedback) {
        Ext.Array.each(deadlines, function(deadline) {
            this._addDeadlineToContainer(deadline, active_feedback);
        }, this);
    }
});
