Ext.define('devilry_subjectadmin.controller.BulkManageDeadlines', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin',
        'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    requires: [
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.form.ErrorUtils',
        'devilry_extjsextras.ConfirmDeleteDialog'
    ],

    views: [
        'bulkmanagedeadlines.BulkManageDeadlinesPanel',
        'bulkmanagedeadlines.DeadlinePanel'
    ],

    models: [
        'Assignment'
    ],

    stores: [
        'DeadlinesBulk',
        'Groups',
        'SearchForGroups'
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
    }, {
        ref: 'normalBodyContainer',
        selector: 'bulkmanagedeadlinespanel #normalBodyContainer'
    }, {
        ref: 'addDeadlineBodyContainer',
        selector: 'bulkmanagedeadlinespanel #addDeadlineBodyContainer'
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
                editDeadline: this._onEditDeadline,
                deleteDeadline: this._onDeleteDeadline
            },

            // Add
            'viewport bulkmanagedeadlinespanel #addDeadlineButton': {
                click: this._onAddDeadline
            },
            'viewport bulkmanagedeadlinespanel bulkmanagedeadlines_createdeadlineform': {
                saveDeadline: this._onSaveNewDeadline,
                cancel: this._onCancelAddNewDeadline,
                fieldvaliditychange: this._onCreateFormFieldValiditityChange
            },
            'viewport bulkmanagedeadlinespanel bulkmanagedeadlines_createdeadlineform #createmodeSpecificGroups': {
                change: this._onCreatemodeSpecificGroupsChange
            },
            'viewport bulkmanagedeadlinespanel bulkmanagedeadlines_createdeadlineform #createmodeSpecificGroupsSelectpanel bulkmanagedeadlines_allgroupsgrid': {
                selectionchange: this._onCreatemodeSpecificGroupsGridSelectionChange
            },

            // Edit
            'viewport bulkmanagedeadlinespanel bulkmanagedeadlines_editdeadlineform': {
                saveDeadline: this._onSaveExistingDeadline,
                cancel: this._onCancelEditExistingDeadline,
                fieldvaliditychange: this._onEditFormFieldValiditityChange
            },
            'viewport bulkmanagedeadlinespanel bulkmanagedeadlines_editdeadlineform #editSpecificGroupsFieldset': {
                expand: this._onExpandEditSpecificGroupsFieldset,
                collapse: this._onCollapseEditSpecificGroupsFieldset
            },
            'viewport bulkmanagedeadlinespanel bulkmanagedeadlines_editdeadlineform bulkmanagedeadlines_groupsindeadlineselectgrid': {
                selectionchange: this._onGroupsInDeadlineSelectionChange
            }
        });
        
        this.mon(this.getDeadlinesBulkStore().proxy, {
            scope: this,
            exception: this._onDeadlinesBulkStoreProxyError
        });
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        this.getBulkManageDeadlinesPanel().setLoading();
        this.assignment_id = this.getBulkManageDeadlinesPanel().assignment_id;
        this.loadAssignment(this.assignment_id);
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

    _setBreadcrumbAndTitle: function(subviewtext) {
        var text = gettext('Deadlines');
        this.setSubviewBreadcrumb(this.assignmentRecord, 'Assignment', [], text);
        var path = this.getPathFromBreadcrumb(this.assignmentRecord);
        this.application.setTitle(Ext.String.format('{0}.{1}', path, text));
    },
    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        this.getSearchForGroupsStore().setAssignment(this.assignmentRecord.get('id'));
        this._setBreadcrumbAndTitle();
    },
    onLoadAssignmentFailure: function(operation) {
        this.onLoadFailure(operation);
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
        } else {
            var add_deadline = this.getBulkManageDeadlinesPanel().add_deadline;
            if(add_deadline) {
                this._onAddDeadline();
            }
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
        component.el.scrollIntoView(this.getBulkManageDeadlinesPanel().getEl(), false, true);
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
            this._setNoDeadlineSelectedHash();
        }
    },

    _setNoDeadlineSelectedHash: function() {
        var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageDeadlines(this.assignment_id);
        this.application.route.setHashWithoutEvent(hash);
    },

    _expandDeadlinePanel: function(deadlinePanel) {
        deadlinePanel.expand();
        Ext.defer(function() {
            this._scrollTo(deadlinePanel);
        }, 300, this);
    },



    //
    //
    // Edit deadline
    //
    //

    _onEditDeadline: function(deadlinePanel, deadlineRecord) {
        var formpanel = deadlinePanel.down('bulkmanagedeadlines_editdeadlineform');
        formpanel.down('alertmessagelist').removeAll(); // NOTE: Remove any error lingering from pressing cancel previously.
        var hash = devilry_subjectadmin.utils.UrlLookup.bulkEditSpecificDeadline(this.assignment_id, deadlineRecord.get('bulkdeadline_id'));
        this.application.route.setHashWithoutEvent(hash);
        this._setActiveDeadlineFormPanel(formpanel);

        deadlinePanel.getLayout().setActiveItem('editDeadline');
        this._scrollTo(formpanel);
        var form = formpanel.getForm();
        form.setValues({
            deadline: deadlineRecord.get('deadline'),
            text: deadlineRecord.get('text')
        });
    },

    _onCancelEditExistingDeadline: function(formpanel) {
        this._unsetActiveDeadlineFormPanel();
        var deadlinePanel = formpanel.up('bulkmanagedeadlines_deadline');
        var deadlineRecord = deadlinePanel.deadlineRecord;
        var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageSpecificDeadline(this.assignment_id, deadlineRecord.get('bulkdeadline_id'));
        deadlinePanel.getLayout().setActiveItem('viewDeadline');
        this.application.route.setHashWithoutEvent(hash);
        this._scrollTo(deadlinePanel);
    },

    _onSaveExistingDeadline: function(formpanel) {
        if(!this._editFormIsValid(formpanel)) {
            return;
        }
        formpanel.setLoading(gettext('Saving') + ' ...');
        var deadlinePanel = formpanel.up('bulkmanagedeadlines_deadline');
        var deadlineRecord = deadlinePanel.deadlineRecord;
        var form = formpanel.getForm();
        var values = form.getFieldValues();
        deadlineRecord.set('deadline', values.deadline);
        deadlineRecord.set('text', values.text);
        if(values.editSpecific) {
            var grid = formpanel.down('bulkmanagedeadlines_groupsindeadlineselectgrid');
            var group_ids = this._getGroupIdsFromGridSelection(grid);
            deadlineRecord.set('group_ids', group_ids);
        }
        deadlineRecord.save({
            scope: this,
            callback: function(updatedDeadlineRecord, operation) {
                formpanel.setLoading(false);
                if(operation.success) {
                    updatedDeadlineRecord.updateBulkDeadlineIdFromOperation(operation);
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

    _onEditFormFieldValiditityChange: function(formpanel) {
        this._enableOrDisableEditFormSavebutton(formpanel);
    },

    _editFormIsValid: function(formpanel) {
        var form = formpanel.getForm();
        if(!form.isValid()) {
            return false;
        }
        if(form.getFieldValues().editSpecific) {
            var grid = formpanel.down('bulkmanagedeadlines_groupsindeadlineselectgrid');
            if(grid.getSelectionModel().getSelection().length === 0) {
                return false;
            }
        }
        return true;
    },

    _enableOrDisableEditFormSavebutton: function(formpanel) {
        var saveButton = formpanel.down('#saveDeadlineButton');
        if(this._editFormIsValid(formpanel)) {
            saveButton.enable();
        } else {
            saveButton.disable();
        }
    },

    _onCollapseEditSpecificGroupsFieldset: function(fieldset) {
        var formpanel = fieldset.up('bulkmanagedeadlines_editdeadlineform');
        this._enableOrDisableEditFormSavebutton(formpanel);
    },

    _onExpandEditSpecificGroupsFieldset: function(fieldset) {
        var grid = fieldset.down('bulkmanagedeadlines_groupsindeadlineselectgrid');
        var bodysize = Ext.getBody().getViewSize();
        grid.setHeight(bodysize.height - 180);
        var formpanel = fieldset.up('bulkmanagedeadlines_editdeadlineform');
        this._scrollTo(formpanel.down('#saveDeadlineButton'));
        grid.getSelectionModel().deselectAll();
        this._enableOrDisableEditFormSavebutton(formpanel);
    },

    _onGroupsInDeadlineSelectionChange: function(selModel, selected) {
        var formpanel = selModel.view.up('bulkmanagedeadlines_editdeadlineform');
        this._enableOrDisableEditFormSavebutton(formpanel);
    },


    //
    //
    // Handle proxy errors
    //
    //

    _setShowNextProxyErrorInWindow: function() {
        this.showNextProxyErrorInWindow = true;
    },
    _unsetShowNextProxyErrorInWindow: function() {
        this.showNextProxyErrorInWindow = false;
    },

    _setActiveDeadlineFormPanel: function(formpanel) {
        this.activeDeadlineFormPanel = formpanel;
    },
    _unsetActiveDeadlineFormPanel: function() {
        this.activeDeadlineFormPanel = undefined;
    },

    _onDeadlinesBulkStoreProxyError: function(proxy, response, operation) {
        var alertmessagelist;
        if(this.activeDeadlineFormPanel) {
            alertmessagelist = this.activeDeadlineFormPanel.down('alertmessagelist');
            alertmessagelist.removeAll();
            this.handleProxyError(alertmessagelist, this.activeDeadlineFormPanel, response, operation);
            this._scrollTo(alertmessagelist);
        } else {
            // NOTE: This should only trigger on load and DELETE error, since saves are
            //       done with _setActiveDeadlineFormPanel()
            alertmessagelist = this.getGlobalAlertmessagelist();
            alertmessagelist.removeAll();
            if(this.showNextProxyErrorInWindow) {
                this._unsetShowNextProxyErrorInWindow();
                this.handleProxyUsingHtmlErrorDialog(response, operation);
            } else {
                this.handleProxyErrorNoForm(alertmessagelist, response, operation);
            }
        }
    },



    //
    //
    // Delete deadline
    //
    //
    
    _onDeleteDeadline: function(deadlinePanel, deadlineRecord) {
        Ext.create('devilry_extjsextras.ConfirmDeleteDialog', {
            width: 400,
            height: 320,
            short_description: Ext.String.format('<strong>{0}</strong>', deadlineRecord.formatDeadline()),
            helptpl: [
                '<p>',
                    gettext('Type {required_confirm_text} in the field below to confirm that you really intend to delete {short_description}.'),
                '</p>',
                '<p>',
                    gettext('Note that deleting a deadlines deletes all deliveries made on that deadline. For this reason, only superusers are permitted to delete deadlines with any deliveries.'),
                '</p>'
            ],

            listeners: {
                scope: this,
                deleteConfirmed: function(deleteDialog) {
                    this._onConfirmDeleteDeadline(deleteDialog, deadlineRecord);
                }
            }
        }).show();
    },

    _onConfirmDeleteDeadline: function(deleteDialog, deadlineRecord) {
        this.getBulkManageDeadlinesPanel().setLoading(gettext('Saving') + ' ...');
        deleteDialog.close();
        this._setShowNextProxyErrorInWindow();
        deadlineRecord.destroy({
            scope: this,
            failure: function() {
                this.getBulkManageDeadlinesPanel().setLoading(false);
                // NOTE: showing the error message is handled in _onDeadlinesBulkStoreProxyError
            },
            success: function() {
                this._unsetShowNextProxyErrorInWindow();
                this._setNoDeadlineSelectedHash();
                deleteDialog.close();
                window.location.reload();
            }
        });
    },


    //
    //
    // Add deadline
    //
    //

    _onAddDeadline: function() {
        this.getNormalBodyContainer().hide();
        this.getAddDeadlineBodyContainer().down('alertmessagelist').removeAll(); // NOTE: We clear the error list, but we keep any values, which makes clicking cancel by mistake less bad.
        this.getAddDeadlineBodyContainer().show();
        this.getAddDeadlineBodyContainer().down('#deadlineField').focus();
        this.getAddDeadlineBodyContainer().down('#createmodeContainer').show();
        var hash = devilry_subjectadmin.utils.UrlLookup.bulkManageAddDeadlines(this.assignment_id);
        this.application.route.setHashWithoutEvent(hash);
    },

    _onCancelAddNewDeadline: function(formpanel) {
        this._unsetActiveDeadlineFormPanel();
        this.getAddDeadlineBodyContainer().hide();
        this.getNormalBodyContainer().show();
        this._setNoDeadlineSelectedHash();
    },

    _onSaveNewDeadline: function(formpanel) {
        if(!this._createFormIsValid(formpanel)) {
            return;
        }
        this._setActiveDeadlineFormPanel(formpanel);
        formpanel.setLoading(gettext('Saving') + ' ...');
        var form = formpanel.getForm();
        var values = form.getFieldValues();
        var deadlineRecord = Ext.create('devilry_subjectadmin.model.DeadlineBulk');
        deadlineRecord.set('deadline', values.deadline);
        deadlineRecord.set('text', values.text);
        deadlineRecord.set('createmode', values.createmode);

        if(values.createmode === 'specific-groups') {
            var grid = formpanel.down('#createmodeSpecificGroupsSelectpanel bulkmanagedeadlines_allgroupsgrid');
            var group_ids = this._getGroupIdsFromGridSelection(grid);
            deadlineRecord.set('group_ids', group_ids);
        }

        deadlineRecord.save({
            scope: this,
            callback: function(updatedDeadlineRecord, operation) {
                formpanel.setLoading(false);
                if(operation.success) {
                    updatedDeadlineRecord.updateBulkDeadlineIdFromOperation(operation);
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

    _getGroupIdsFromGridSelection: function(grid) {
        var selected = grid.getSelectionModel().getSelection();
        var group_ids = [];
        Ext.Array.each(selected, function(groupRecord) {
            group_ids.push(groupRecord.get('id'));
        }, this);
        return group_ids;
    },


    _onCreateFormFieldValiditityChange: function(formpanel) {
        this._enableOrDisableCreateFormSavebutton(formpanel);
    },

    _createFormIsValid: function(formpanel) {
        var form = formpanel.getForm();
        if(!form.isValid()) {
            return false;
        }

        var createmode = form.getFieldValues().createmode;
        if(Ext.isArray(createmode)) {
            // NOTE: createmode is an array of the old and new value when change-events on the radiogroup triggers. The new value is the second element in the array
            createmode = createmode[1];
        }
        if(createmode === 'specific-groups') {
            var grid = formpanel.down('bulkmanagedeadlines_allgroupsgrid');
            if(grid.getSelectionModel().getSelection().length === 0) {
                return false;
            }
        }
        return true;
    },

    _enableOrDisableCreateFormSavebutton: function(formpanel) {
        var saveButton = formpanel.down('#saveDeadlineButton');
        if(this._createFormIsValid(formpanel)) {
            saveButton.enable();
        } else {
            saveButton.disable();
        }
    },


    //
    //
    // Createmode specific-groups
    //
    //
    _onCreatemodeSpecificGroupsChange: function(field, isSelected) {
        var formpanel = field.up('bulkmanagedeadlines_createdeadlineform');
        this._enableOrDisableCreateFormSavebutton(formpanel);
        if(isSelected) {
            this._onCreatemodeSpecificGroupsSelect(formpanel);
        } else {
            this._onCreatemodeSpecificGroupsDeSelect(formpanel);
        }
    },
    _onCreatemodeSpecificGroupsDeSelect: function(formpanel) {
        formpanel.down('#createmodeSpecificGroupsSelectpanel').hide();
    },
    _onCreatemodeSpecificGroupsSelect: function(formpanel) {
        var selectPanel = formpanel.down('#createmodeSpecificGroupsSelectpanel');
        selectPanel.show();
        if(!this.getGroupsStore().isLoading()) {
            this._loadGroupsStore();
        }

        // Adjust size of the grid to make sure it fits within the window, and scroll to the grid
        var grid = selectPanel.down('bulkmanagedeadlines_allgroupsgrid');
        var bodysize = Ext.getBody().getViewSize();
        grid.setHeight(bodysize.height - 170);
//        this._scrollTo(formpanel.down('#saveDeadlineButton')); // NOTE: Seems to cause rendering issues, at least in Chrome
    },

    _loadGroupsStore: function(groupIdsToSelectOnLoad) {
        this.getGroupsStore().loadGroupsInAssignment(this.assignmentRecord.get('id'), {
            scope: this,
            callback: function(records, operation) {
                if(operation.success) {
                    this._onLoadGroupsStoreSuccess(groupIdsToSelectOnLoad);
                } else {
                    this._onLoadGroupsStoreFailure(operation);
                }
            }
        });
    },
    _onLoadGroupsStoreSuccess: function(groupIdsToSelectOnLoad) {
        //console.log('Success');
    },
    _onLoadGroupsStoreFailure: function(operation) {
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        error.addErrors(null, operation);
        var errormessage = error.asHtmlList();
        Ext.widget('htmlerrordialog', {
            title: gettext('Failed to load groups'),
            bodyHtml: errormessage
        }).show();
    },

    _onCreatemodeSpecificGroupsGridSelectionChange: function(selModel) {
        var formpanel = selModel.view.up('bulkmanagedeadlines_createdeadlineform');
        this._enableOrDisableCreateFormSavebutton(formpanel);
    }
});
