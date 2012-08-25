Ext.define('devilry_student.controller.GroupInfo', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.window.MessageBox',
        'devilry_student.view.add_delivery.AddDeliveryPanel',
        'Ext.fx.Animator',
        'devilry_extjsextras.AlertMessage'
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
                active_feedback_link_clicked: this._onActiveFeedbackLink,
                delivery_link_clicked: this._onDeliveryLink
            },
            'viewport groupinfo groupinfo_delivery #feedback': {
                render: this._onFeedbackRender
            }
        });
    },

    _onRender: function() {
        this._reload();
    },

    _reload: function() {
        var group_id = this.getOverview().group_id;
        this.getOverview().setLoading(true);
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
        this.getOverview().setLoading(false);
    },

    _onGroupInfoLoadFailure: function(record, operation) {
        var message = gettext('Failed to load group. Try to reload the page');
        if(operation.error.status === 403) {
            message = gettext('Permission denied.');
        }
        this.getOverview().setLoading(false);
        this._showLoadError(message);
    },

    _showLoadError: function(message) {
        //Ext.MessageBox.alert(gettext('Error'), message);
        this.getOverview().removeAll();
        this.getOverview().add({
            xtype: 'alertmessage',
            margin: 40,
            type: 'error',
            title: gettext('Error'),
            message: message
        });
    },

    _populateDeadlinesContainer: function(deadlines, active_feedback) {
        var container = this.getDeadlinesContainer();
        container.removeAll();
        if(deadlines.length == 0) {
            container.add({
                xtype: 'alertmessage',
                type: 'error',
                title: interpolate(gettext('No %(deadlines_term)s'), {
                    deadlines_term: gettext('deadlines')
                }, true),
                message: interpolate(gettext('You have no %(deadlines_term)s, so you can not add any %(deliveries_term)s.'), {
                    deadlines_term: gettext('deadlines'),
                    deliveries_term: gettext('deliveries')
                }, true)
            });
        } else {
            Ext.Array.each(deadlines, function(deadline) {
                container.add({
                    xtype: 'groupinfo_deadline',
                    deadline: deadline,
                    active_feedback: active_feedback
                });
            }, this);
        }
    },

    _populateTitleBox: function(groupInfoRecord) {
        this.getTitleBox().update({
            groupinfo: groupInfoRecord.data
        });
    },

    _deliveriesAsFlatArray: function(groupInfoRecord) {
        var deliveries = [];
        Ext.Array.each(groupInfoRecord.get('deadlines'), function(deadline) {
            deliveries = deliveries.concat(deadline.deliveries);
        }, this);
        return deliveries;
    },

    _populateMetadata: function(groupInfoRecord) {
        this.getMetadataContainer().removeAll();
        this.getMetadataContainer().add({
            xtype: 'groupmetadata',
            data: {
                groupinfo: groupInfoRecord.data,
                can_add_deliveries: groupInfoRecord.can_add_deliveries(),
                hard_deadline_expired: groupInfoRecord.hard_deadline_expired(),
                examiner_term: gettext('examiner'),
                deliveries: this._deliveriesAsFlatArray(groupInfoRecord)
            }
        });
    },

    _selectDelivery: function(delivery_id) {
        this._hightlightSelectedDelivery(delivery_id);
        var group_id = this.groupInfoRecord.get('id');
        this.application.route.setHashWithoutEvent(Ext.String.format('/group/{0}/{1}', group_id, delivery_id));
    },

    _onActiveFeedbackLink: function() {
        var delivery_id = this.groupInfoRecord.get('active_feedback').delivery_id;
        this._selectDelivery(delivery_id);
    },

    _onDeliveryLink: function(delivery_id) {
        this._selectDelivery(delivery_id);
    },

    _hightlightSelectedDelivery: function(delivery_id) {
        var itemid = Ext.String.format('#delivery-{0}', delivery_id);
        var deliveryPanel = this.getOverview().down(itemid);
        if(deliveryPanel) {
            var container = deliveryPanel.up('groupinfo_deadline');
            container.expand();
            //deliveryPanel.el.scrollIntoView(this.getOverview().body, false, true);
            deliveryPanel.el.scrollIntoView(this.getDeadlinesContainer().body, false, true);
            //deliveryPanel.body.setStyle({
                //'background-color': 'red'
            //});
            Ext.create('Ext.fx.Animator', {
                target: deliveryPanel.body,
                duration: 3000,
                keyframes: {
                    0: {
                        backgroundColor: '#FFFFFF'
                    },
                    20: {
                        backgroundColor: '#FBEED5'
                    },
                    50: {
                        backgroundColor: '#FBEED5'
                    },
                    100: {
                        backgroundColor: '#FFFFFF'
                    }
                }
            });
        } else {
            this._showLoadError(interpolate(gettext('Invalid delivery: %s'), [delivery_id]));
        }
    },

    _setBreadcrumbs: function(groupInfoRecord, extra) {
        var subject = groupInfoRecord.get('breadcrumbs').subject;
        var period = groupInfoRecord.get('breadcrumbs').period;
        var assignment = groupInfoRecord.get('breadcrumbs').assignment;
        var periodpath = [subject.short_name, period.short_name].join('.');

        var breadcrumbs = [{
            url: '#/browse/',
            text: gettext('Browse')
        }, {
            url: Ext.String.format('#/browse/{0}', period.id),
            text: periodpath
        }];

        if(extra) {
            breadcrumbs.push({
                url: Ext.String.format('#/group/{0}/', groupInfoRecord.get('id')),
                text: assignment.short_name
            });
            this.application.breadcrumbs.set(breadcrumbs, extra);
        } else {
            this.application.breadcrumbs.set(breadcrumbs, assignment.short_name);
        }

        var title = [periodpath, assignment.shortname].join('.');
        if(extra) {
            title += ' - ' + extra;
        }
        this.application.setTitle(title);
    },

    _addDelivery: function() {
        if(!this.groupInfoRecord.get('is_open')) {
            this._showLoadError(interpolate(gettext('Can not add %(deliveries_term)s on closed groups.'), {
                deliveries_term: gettext('deliveries')
            }, true));
            return;
        }
        var deadlines = this.groupInfoRecord.get('deadlines');
        var latest_deadline = this._getLatestDeadline();
        if(typeof latest_deadline == 'undefined') {
            this._showLoadError(interpolate(gettext('Can not add %(deliveries_term)s on a group without a %(deadline_term)s.'), {
                deliveries_term: gettext('deliveries'),
                deadline_term: gettext('deadline')
            }, true));
            return;
        }
        var deadlinePanel = this._getDeadlinePanelById(latest_deadline.id);
        deadlinePanel.down('#addDeliveryPanelContainer').removeAll();
        deadlinePanel.down('#addDeliveryPanelContainer').add({
            xtype: 'add_delivery',
            groupInfoRecord: this.groupInfoRecord,
            listeners: {
                scope: this,
                deliveryCancelled: this._onAddDeliveryCancel,
                deliveryFinished: this._onAddDeliveryFinished
            }
        });
        this._setBreadcrumbs(this.groupInfoRecord, interpolate(gettext('Add %(delivery_term)s'), {
            delivery_term: gettext('delivery')
        }, true));
        this._focusOnAddDeliveryPanel();
    },

    _removeAddDeliveriesPanel: function(delivery_id) {
        this._removeFocusFromDeliveryPanel();
        var token = Ext.String.format('/group/{0}/{1}', this.groupInfoRecord.get('id'), delivery_id || '');
        this.application.route.navigate(token);
    },

    _focusOnAddDeliveryPanel: function() {
        Ext.Array.each(this.getDeadlinesContainer().query('groupinfo_deadline'), function(panel) {
            panel.hide();
        }, this);
        var latest_deadline = this._getLatestDeadline();
        var deadlinePanel = this._getDeadlinePanelById(latest_deadline.id);
        deadlinePanel.show();
        deadlinePanel.expand();
        deadlinePanel.hideDeliveries();
        this.getMetadataContainer().hide();
    },

    _removeFocusFromDeliveryPanel: function() {
        Ext.Array.each(this.getDeadlinesContainer().query('groupinfo_deadline'), function(panel) {
            panel.show();
            panel.collapse();
        }, this);
        var deadlinePanel = this._getDeadlinePanelById(this._getLatestDeadline().id)
        deadlinePanel.down('#addDeliveryPanelContainer').removeAll();
        deadlinePanel.showDeliveries();
        this.getMetadataContainer().show();
    },

    _onAddDeliveryCancel: function() {
        this._removeAddDeliveriesPanel();
    },

    _onAddDeliveryFinished: function(delivery_id) {
        this._removeAddDeliveriesPanel(delivery_id);
    },

    _getLatestDeadline: function() {
        var deadlines = this.groupInfoRecord.get('deadlines');
        if(deadlines.length == 0) {
            return undefined;
        } else {
            return deadlines[0];
        }
    },

    _getDeadlinePanelById: function(deadline_id) {
        var selector = Ext.String.format('#deadline-{0}', deadline_id);
        return this.getOverview().down(selector);
    },

    _onFeedbackRender: function(component) {
        MathJax.Hub.Queue(["Typeset", MathJax.Hub, component.el.id]);
    }
});
