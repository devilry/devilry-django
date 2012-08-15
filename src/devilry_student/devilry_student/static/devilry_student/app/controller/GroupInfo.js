Ext.define('devilry_student.controller.GroupInfo', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.window.MessageBox'
    ],

    views: [
        'groupinfo.Overview',
        'groupinfo.DeadlinePanel',
        'groupinfo.DeliveryPanel',
        'groupinfo.GroupMetadata'
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
        this._populateDeadlinesContainer(groupInfoRecord.get('deadlines'), groupInfoRecord.get('active_feedback'));
        this._populateMetadata(groupInfoRecord);
        this._populateTitleBox(groupInfoRecord);
        var delivery_id = this.getOverview().delivery_id;
        this.groupInfoRecord = groupInfoRecord;
        if(delivery_id != undefined) {
            this._hightlightSelectedDelivery(delivery_id);
        }
    },

    _onGroupInfoLoadFailure: function() {
        this._showLoadError(gettext('Failed to load group. Try to reload the page'));
    },

    _showLoadError: function(message) {
        Ext.MessageBox.alert(gettext('Error'), message);
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
        this._hightlightSelectedDelivery(this.groupInfoRecord.get('active_feedback').delivery_id);
    },

    _hightlightSelectedDelivery: function(delivery_id) {
        var itemid = Ext.String.format('#delivery-{0}', delivery_id);
        var deliveryPanel = this.getOverview().down(itemid);
        if(deliveryPanel) {
            var container = deliveryPanel.up('groupinfo_deadline');
            container.expand();
            deliveryPanel.el.scrollIntoView(this.getOverview().body, false, true);
        } else {
            this._showLoadError(interpolate(gettext('Invalid delivery: %s'), [delivery_id]));
        }
    }
});
