Ext.define('devilry_student.controller.GroupInfo', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.window.MessageBox'
    ],

    views: [
        'groupinfo.Overview',
        'groupinfo.DeadlinePanel',
        'groupinfo.DeliveryPanel',
        'groupinfo.GroupMetadata',
        'groupinfo.AddDeliveryPanel'
    ],

    models: ['GroupInfo'],

    refs: [{
        ref: 'overview',
        selector: 'viewport groupinfo'
    }, {
        ref: 'deadlinesContainer',
        selector: 'viewport groupinfo #deadlinesContainer'
    }, {
        ref: 'metadataContainer',
        selector: 'viewport groupinfo #metadataContainer'
    }, {
        ref: 'titleBox',
        selector: 'viewport groupinfo #titleBox'
    }],

    init: function() {
        this.control({
            'viewport groupinfo #deadlinesContainer': {
                render: this._onRender
            },
            'viewport groupinfo groupmetadata': {
                active_feedback_link_clicked: this._onActiveFeedbackLink
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
        this._setBreadcrumbs(groupInfoRecord);
        this._populateDeadlinesContainer(groupInfoRecord.get('deadlines'), groupInfoRecord.get('active_feedback'));
        this._populateMetadata(groupInfoRecord);
        this._populateTitleBox(groupInfoRecord);
        this.groupInfoRecord = groupInfoRecord;

        var delivery_id = this.getOverview().delivery_id;
        if(delivery_id != undefined) {
            this._hightlightSelectedDelivery(delivery_id);
        }

        if(this.getOverview().add_delivery) {
            this._addDelivery();
        }
    },

    _onGroupInfoLoadFailure: function() {
        this._showLoadError(gettext('Failed to load group. Try to reload the page'));
    },

    _showLoadError: function(message) {
        Ext.MessageBox.alert(gettext('Error'), message);
    },

    _populateDeadlinesContainer: function(deadlines, active_feedback) {
        Ext.Array.each(deadlines, function(deadline) {
            this.getDeadlinesContainer().add({
                xtype: 'groupinfo_deadline',
                deadline: deadline,
                active_feedback: active_feedback
            });
        }, this);
    },

    _populateTitleBox: function(groupInfoRecord) {
        this.getTitleBox().update({
            groupinfo: groupInfoRecord.data
        });
    },

    _populateMetadata: function(groupInfoRecord) {
        this.getMetadataContainer().removeAll();
        this.getMetadataContainer().add({
            xtype: 'groupmetadata',
            data: {
                groupinfo: groupInfoRecord.data,
                examiner_term: gettext('examiner')
            }
        });
    },

    _onActiveFeedbackLink: function() {
        var group_id = this.groupInfoRecord.get('id');
        var delivery_id = this.groupInfoRecord.get('active_feedback').delivery_id;
        this._hightlightSelectedDelivery(delivery_id);
        this.application.route.setHashWithoutEvent(Ext.String.format('/group/{0}/{1}', group_id, delivery_id));
    },

    _hightlightSelectedDelivery: function(delivery_id) {
        var itemid = Ext.String.format('#delivery-{0}', delivery_id);
        var deliveryPanel = this.getOverview().down(itemid);
        if(deliveryPanel) {
            var container = deliveryPanel.up('groupinfo_deadline');
            container.expand();
            //deliveryPanel.el.scrollIntoView(this.getOverview().body, false, true);
            deliveryPanel.el.scrollIntoView(this.getDeadlinesContainer().body, false, true);
        } else {
            this._showLoadError(interpolate(gettext('Invalid delivery: %s'), [delivery_id]));
        }
    },

    _setBreadcrumbs: function(groupInfoRecord) {
        var subject = groupInfoRecord.get('breadcrumbs').subject;
        var period = groupInfoRecord.get('breadcrumbs').period;
        var assignment = groupInfoRecord.get('breadcrumbs').assignment;
        var periodpath = [subject.short_name, period.short_name].join('.');

        this.application.breadcrumbs.set([{
            url: '#/browse/',
            text: gettext('Browse')
        }, {
            url: Ext.String.format('#/browse/{0}', period.id),
            text: periodpath
        }], assignment.short_name);

        var path = [periodpath, assignment.shortname].join('.');
        this.application.setTitle(path);
    },

    _addDelivery: function() {
        console.log('Make delivery');
        if(!this.groupInfoRecord.get('is_open')) {
            // NOTE: We use an error message since the user do not get this through normal UI navigation
            this._showLoadError(interpolate(gettext('Can not add %(deliveries_term)s on closed groups.'), {
                deliveries_term: gettext('deliveries')
            }, true));
            return;
        }
        var deadlines = this.groupInfoRecord.get('deadlines');
        if(deadlines.length == 0) {
            // NOTE: We use an error message since the user do not get this through normal UI navigation
            this._showLoadError(interpolate(gettext('Can not add %(deliveries_term)s on groups without a deadline.'), {
                deliveries_term: gettext('deliveries')
            }, true));
        }
        var latest_deadline = deadlines[0];
        var deadlinePanel = this._getDeadlinePanelById(latest_deadline.id);
        deadlinePanel.down('#addDeliveryPanelContainer').removeAll();
        deadlinePanel.down('#addDeliveryPanelContainer').add({
            xtype: 'groupinfo_add_delivery',
            groupInfoRecord: this.groupInfoRecord
        });
        deadlinePanel.expand();
        deadlinePanel.hideDeliveries();
    },

    _getDeadlinePanelById: function(deadline_id) {
        var selector = Ext.String.format('#deadline-{0}', deadline_id);
        return this.getOverview().down(selector);
    }
});
