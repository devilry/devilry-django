Ext.define('devilry_student.controller.Dashboard', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.window.MessageBox'
    ],

    views: [
        'dashboard.Overview',
        'dashboard.OpenGroupsDeadlineExpiredGrid',
        'dashboard.OpenGroupsDeadlineNotExpiredGrid',
        'dashboard.RecentDeliveriesGrid',
        'dashboard.RecentFeedbacksGrid'
    ],

    stores: [
        'OpenGroupsDeadlineNotExpired',
        'OpenGroupsDeadlineExpired',
        'RecentDeliveries',
        'RecentFeedbacks'
    ],

    refs: [{
        ref: 'overview',
        selector: 'viewport dashboard'
    }],

    init: function() {
        this.control({
            'viewport dashboard': {
                render: this._onRenderDashboard
            },
        });
    },

    _handleGroupLoadError: function(message) {
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: message,
            icon: Ext.MessageBox.ERROR,
            buttons: Ext.MessageBox.OK
        });
    },

    _onRenderDashboard: function() {
        this.getOpenGroupsDeadlineExpiredStore().load({
            callback: function(records, operation) {
                if(!operation.success) {
                    this._handleGroupLoadError(gettext('Failed to load your assignments. Please try to reload the page.'));
                }
            }
        });
        this.getOpenGroupsDeadlineNotExpiredStore().load({
            callback: function(records, operation) {
                if(!operation.success) {
                    this._handleGroupLoadError(gettext('Failed to load your assignments. Please try to reload the page.'));
                }
            }
        });
        this.getRecentDeliveriesStore().load({
            callback: function(records, operation) {
                if(!operation.success) {
                    this._handleGroupLoadError(gettext('Failed to load your recent deliveries. Please try to reload the page.'));
                }
            }
        });
        this.getRecentFeedbacksStore().load({
            callback: function(records, operation) {
                if(!operation.success) {
                    this._handleGroupLoadError(gettext('Failed to load your recent feedbacks. Please try to reload the page.'));
                }
            }
        });
    }
});
