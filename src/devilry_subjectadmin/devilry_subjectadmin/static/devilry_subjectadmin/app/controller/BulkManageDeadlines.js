Ext.define('devilry_subjectadmin.controller.BulkManageDeadlines', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    requires: [
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.form.ErrorUtils'
    ],

    views: [
        'bulkmanagedeadlines.BulkManageDeadlinesPanel',
        'bulkmanagedeadlines.DeadlinePanel'
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
            'viewport bulkmanagedeadlinespanel #addDeadlineButton': {
                click: this._onAddDeadline
            },
            'viewport bulkmanagedeadlinespanel bulkmanagedeadlines_deadline bulkmanagedeadlines_deadlineform': {
                saveDeadline: this._onSaveExistingDeadline,
                cancel: this._onCancelEditExistingDeadline
            }
        });
        
        this.mon(this.getDeadlinesBulkStore().proxy, {
            scope: this,
            exception: this._onDeadlinesBulkStoreProxyError
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
                    // NOTE: Failure is handled in _onDeadlinesBulkStoreProxyError()
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
            this._expandDeadlinePanel(deadlinePanel);
            var edit_deadline = this.getBulkManageDeadlinesPanel().edit_deadline;
            if(edit_deadline) {
                this._onEditDeadline(deadlinePanel, deadlinePanel.deadlineRecord);
            }
        }
    },

    _scrollTo: function(component) {
        component.el.scrollIntoView(this.getBulkManageDeadlinesPanel().body, false, true);
    },

    _onDeadlineHeaderClick: function(header) {
        var deadlinePanel = header.up('bulkmanagedeadlines_deadline');
        var isCollapsed = deadlinePanel.getCollapsed();
        if(isCollapsed) {
            var deadlineRecord = deadlinePanel.deadlineRecord;
            var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageSpecificDeadline(this.assignment_id, deadlineRecord.get('bulkdeadline_id'));
            this.application.route.setHashWithoutEvent(hash);
            this._expandDeadlinePanel(deadlinePanel);
        } else {
            deadlinePanel.collapse();
            var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageDeadlines(this.assignment_id);
            this.application.route.setHashWithoutEvent(hash);
        }
    },

    _expandDeadlinePanel: function(deadlinePanel) {
        deadlinePanel.expand();
        Ext.defer(function() {
            this._scrollTo(deadlinePanel);
        }, 300, this);
    },


    _onEditDeadline: function(deadlinePanel, deadlineRecord) {
        var formpanel = deadlinePanel.down('bulkmanagedeadlines_deadlineform');
        var hash = devilry_subjectadmin.utils.UrlLookup.bulkEditSpecificDeadline(this.assignment_id, deadlineRecord.get('bulkdeadline_id'));
        this.application.route.setHashWithoutEvent(hash);
        this._setActiveDeadlineFormPanel(formpanel);

        deadlinePanel.down('#editDeadlineButton').hide();
        formpanel.show();
        this._scrollTo(formpanel);
        var form = formpanel.getForm();
        form.setValues({
            deadline: deadlineRecord.get('deadline'),
            text: deadlineRecord.get('text')
        });
    },

    _setActiveDeadlineFormPanel: function(formpanel) {
        this.activeDeadlineFormPanel = formpanel;
    },
    _unsetActiveDeadlineFormPanel: function() {
        this.activeDeadlineFormPanel = undefined;
    },

    _onCancelEditExistingDeadline: function(formpanel) {
        formpanel.hide();
        this._unsetActiveDeadlineFormPanel();
        var deadlinePanel = formpanel.up('bulkmanagedeadlines_deadline');
        var deadlineRecord = deadlinePanel.deadlineRecord;
        var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageSpecificDeadline(this.assignment_id, deadlineRecord.get('bulkdeadline_id'));
        deadlinePanel.down('#editDeadlineButton').show();
        this.application.route.setHashWithoutEvent(hash);
        this._scrollTo(deadlinePanel);
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
                    console.log(updatedDeadlineRecord.get('bulkdeadline_id'));
                    updatedDeadlineRecord.updateBulkDeadlineIdFromOperation(operation);
                    console.log('updated:', updatedDeadlineRecord.get('bulkdeadline_id'));
                    var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageSpecificDeadline(
                        this.assignment_id, updatedDeadlineRecord.get('bulkdeadline_id'));
                    this.application.route.setHashWithoutEvent(hash);
                    window.location.reload();
                } else {
                    // NOTE: Failure is handled in _onDeadlinesBulkStoreProxyError()
                }
            }
        });
    },

    _onSaveExistingDeadlineError: function(formpanel, operation) {
        var alertmessagelist = formpanel.down('alertmessagelist');
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(operation.response, operation);
        alertmessagelist.addMany(errorhandler.errormessages, 'error');
        devilry_extjsextras.form.ErrorUtils.addFieldErrorsToAlertMessageList(formpanel,
            errorhandler.fielderrors, alertmessagelist);
        devilry_extjsextras.form.ErrorUtils.markFieldErrorsAsInvalid(formpanel,
            errorhandler.fielderrors);
    },

    _onDeadlinesBulkStoreProxyError: function(proxy, response, operation) {
        if(this.activeDeadlineFormPanel) {
            var alertmessagelist = this.activeDeadlineFormPanel.down('alertmessagelist');
            alertmessagelist.removeAll();
            this.handleProxyError(alertmessagelist, this.activeDeadlineFormPanel, response, operation);
            this._scrollTo(alertmessagelist);
        } else {
            // NOTE: This should only trigger on load error, since saves are
            //       done with _setActiveDeadlineFormPanel()
            var alertmessagelist = this.getGlobalAlertmessagelist();
            alertmessagelist.removeAll();
            this.handleProxyErrorNoForm(alertmessagelist, response, operation);
        }
    },

    _onAddDeadline: function() {
        Ext.widget('window', {
            title: interpolate(gettext('Add %(deadline_term)s'), {
                deadline_term: gettext('deadline')
            }, true),
            layout: 'fit',
            closable: true,
            width: 600,
            height: 400,
            items: {
                xtype: 'bulkmanagedeadlines_deadlineform',
                listeners: {
                    scope: this,
                    cancel: function(formpanel) {
                        formpanel.up('window').close();
                    },
                    saveDeadline: this._onAddDeadlineSave
                }
            }
        }).show();
    },

    _onAddDeadlineSave: function(formpanel) {
        formpanel.setLoading(gettext('Saving') + ' ...');
        var form = formpanel.getForm();
        var values = form.getFieldValues();
        console.log(values);
        var deadlineRecord = Ext.create('devilry_subjectadmin.model.DeadlineBulk');
        deadlineRecord.set('deadline', values.deadline);
        deadlineRecord.set('text', values.text);
        console.log(deadlineRecord);
        deadlineRecord.save({
            scope: this,
            callback: function(updatedDeadlineRecord, operation) {
                formpanel.setLoading(false);
                if(operation.success) {
                    console.log(updatedDeadlineRecord.get('bulkdeadline_id'));
                    updatedDeadlineRecord.updateBulkDeadlineIdFromOperation(operation);
                    console.log('updated:', updatedDeadlineRecord.get('bulkdeadline_id'));
                    var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageSpecificDeadline(
                        this.assignment_id, updatedDeadlineRecord.get('bulkdeadline_id'));
                    this.application.route.setHashWithoutEvent(hash);
                    window.location.reload();
                } else {
                    // NOTE: Failure is handled in _onDeadlinesBulkStoreProxyError()
                }
            }
        });
    }
});
