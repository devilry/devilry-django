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
        console.log('render');
        var group_id = this.getOverview().group_id;
        console.log(group_id);
        this.getGroupInfoModel().load(group_id, {
            scope: this,
            success: this._onGroupInfoLoadSuccess,
            failure: this._onGroupInfoLoadFailure
        });
    },

    _onGroupInfoLoadSuccess: function(groupInfoRecord) {
        console.log(groupInfoRecord.data);
        this._populateDeadlinesContainer(groupInfoRecord.get('deadlines'));
    },

    _onGroupInfoLoadFailure: function() {
        Ext.MessageBox.alert(gettext('Error'),
            gettext('Failed to load group. Try to reload the page'));
    },

    _addDeadlineToContainer: function(deadline) {
        console.log(deadline);
        this.getDeadlinesContainer().add({
            xtype: 'groupinfo_deadline',
            deadline: deadline
        });
    },

    _populateDeadlinesContainer: function(deadlines) {
        Ext.Array.each(deadlines, function(deadline) {
            this._addDeadlineToContainer(deadline);
        }, this);
    }
});
