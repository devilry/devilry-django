Ext.define('devilry_subjectadmin.controller.BulkManageDeadlines', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin'
    ],

    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    views: [
        'bulkmanagedeadlines.BulkManageDeadlinesPanel',
        'bulkmanagedeadlines.DeadlinePanel'
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
        ref: 'deadlinesContainer',
        selector: 'bulkmanagedeadlinespanel #deadlinesContainer'
    }, {
        ref: 'globalAlertmessagelist',
        selector: 'bulkmanagedeadlinespanel #globalAlertmessagelist'
    }],

    init: function() {
        this.control({
            'viewport bulkmanagedeadlinespanel #globalAlertmessagelist': {
                render: this._onRender
            },
            'viewport bulkmanagedeadlinespanel bulkmanagedeadlines_deadline header': {
                click: this._onDeadlineHeaderClick
            },
            'viewport bulkmanagedeadlinespanel bulkmanagedeadlines_deadline': {
                editDeadline: this._onEditDeadline
            },
            'viewport bulkmanagedeadlinespanel bulkmanagedeadlines_deadline bulkmanagedeadlines_deadlineform': {
                saveDeadline: this._onSaveExistingDeadline,
                cancel: this._onCancelEditExistingDeadline
            }
        });
    },

    _onRender: function() {
        this.getBulkManageDeadlinesPanel().setLoading();
        this.assignment_id = this.getBulkManageDeadlinesPanel().assignment_id;
        var store = this.getDeadlinesBulkStore();
        store.proxy.setUrl(this.assignment_id);
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

    _onLoadSuccess: function(deadlineRecords, operation) {
        this._populateDeadlinesContainer(deadlineRecords);
    },

    _populateDeadlinesContainer: function(deadlineRecords) {
        var deadlinepanels_rendered = 0;
        Ext.Array.each(deadlineRecords, function(deadlineRecord) {
            this.getDeadlinesContainer().add({
                xtype: 'bulkmanagedeadlines_deadline',
                deadlineRecord: deadlineRecord,
                assignment_id: this.assignment_id,
                listeners: {
                    scope: this,
                    single: true,
                    render: function(panel, eOpts) {
                        deadlinepanels_rendered ++;
                        if(deadlinepanels_rendered == deadlineRecords.length) {
                            Ext.defer(function() {
                                this._onAllDeadlinePanelsRendered();
                            }, 200, this);
                        }
                    }
                }
            });
        }, this);
    },

    _onAllDeadlinePanelsRendered: function() {
        var bulkdeadline_id = this.getBulkManageDeadlinesPanel().bulkdeadline_id;
        if(typeof bulkdeadline_id !== 'undefined') {
            this._expandDeadlineById(bulkdeadline_id);
        }
    },

    _expandDeadlineById: function(id) {
        var itemid = Ext.String.format('#deadline-{0}', id);
        var deadlinePanel = this.getDeadlinesContainer().down(itemid);
        if(deadlinePanel) {
            deadlinePanel.expand();
            this._scrollToDeadlinepanel(deadlinePanel);
            var edit_deadline = this.getBulkManageDeadlinesPanel().edit_deadline;
            if(edit_deadline) {
                this._onEditDeadline(deadlinePanel, deadlinePanel.deadlineRecord);
            }
        }
    },

    _scrollToDeadlinepanel: function(deadlinePanel) {
        deadlinePanel.el.scrollIntoView(this.getBulkManageDeadlinesPanel().body, false, true);
    },

    _onDeadlineHeaderClick: function(header) {
        var deadlinePanel = header.up('bulkmanagedeadlines_deadline');
        var isCollapsed = deadlinePanel.getCollapsed();
        if(isCollapsed) {
            this._expandDeadlinePanel(deadlinePanel);
        } else {
            deadlinePanel.collapse();
            var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageDeadlines(this.assignment_id);
            this.application.route.setHashWithoutEvent(hash);
        }
    },

    _expandDeadlinePanel: function(deadlinePanel) {
        deadlinePanel.expand();
        var deadlineRecord = deadlinePanel.deadlineRecord;
        var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageSpecificDeadline(this.assignment_id, deadlineRecord.get('bulkdeadline_id'));
        this.application.route.setHashWithoutEvent(hash);
        Ext.defer(function() {
            this._scrollToDeadlinepanel(deadlinePanel);
        }, 300, this);
    },


    _onEditDeadline: function(deadlinePanel, deadlineRecord) {
        var formpanel = deadlinePanel.down('bulkmanagedeadlines_deadlineform');
        var hash = devilry_subjectadmin.utils.UrlLookup.bulkEditSpecificDeadline(this.assignment_id, deadlineRecord.get('bulkdeadline_id'));
        this.application.route.setHashWithoutEvent(hash);

        this._expandDeadlinePanel(deadlinePanel);
        formpanel.show();
        var form = formpanel.getForm();
        form.setValues({
            deadline: deadlineRecord.get('deadline'),
            text: deadlineRecord.get('text')
        });
    },

    _onCancelEditExistingDeadline: function(formpanel) {
        formpanel.hide();
        var deadlineRecord = formpanel.up('bulkmanagedeadlines_deadline').deadlineRecord;
        var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageSpecificDeadline(this.assignment_id, deadlineRecord.get('bulkdeadline_id'));
        this.application.route.setHashWithoutEvent(hash);
    },

    _onSaveExistingDeadline: function(formpanel) {
        formpanel.setLoading(gettext('Saving') + ' ...');
        var deadlinePanel = formpanel.up('bulkmanagedeadlines_deadline');
        var deadlineRecord = deadlinePanel.deadlineRecord;
        var form = formpanel.getForm();
        var values = form.getFieldValues();
        deadlineRecord.set('deadline', values.deadline);
        deadlineRecord.set('text', values.text);
        deadlineRecord.save({
            scope: this,
            callback: function(updatedDeadlineRecord, operation) {
                formpanel.setLoading(false);
                if(operation.success) {
                    var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageSpecificDeadline(
                        this.assignment_id, updatedDeadlineRecord.get('bulkdeadline_id'));
                    this.application.route.navigate(hash);
                } else {
                    console.log('save failed', operation);
                }
            }
        });
    }
});
