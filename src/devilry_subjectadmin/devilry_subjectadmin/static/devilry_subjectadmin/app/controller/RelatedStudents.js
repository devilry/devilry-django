/**
 * Controller for the related students view
 */
Ext.define('devilry_subjectadmin.controller.RelatedStudents', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'relatedstudents.Overview'
    ],

    stores: ['RelatedStudents'],
    models: ['Period'],

    requires: [
        'devilry_subjectadmin.utils.UrlLookup',
        'Ext.window.MessageBox'
    ],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
    }, {
        ref: 'overview',
        selector: 'viewport relatedstudents'
    }, {
        ref: 'grid',
        selector: 'viewport relatedstudentsgrid'
    }, {
        ref: 'sidebarDeck',
        selector: 'viewport relatedstudents #sidebarDeck'
    }, {
        ref: 'autocompleteUserWidget',
        selector: 'viewport relatedstudents autocompleteuserwidget'
    }],

    init: function() {
        this.control({
            'viewport relatedstudents': {
                render: this._onRender
            },

            // Remove students
            'viewport relatedstudents #removeButton': {
                click: this._onRemoveSelected
            },

            // Add student
            'viewport relatedstudents #addButton': {
                click: this._onGridAddButton
            },
            'viewport relatedstudents selectrelateduserpanel': {
                cancel: this._resetToHelpView
            },
            'viewport relatedstudents selectrelateduserpanel autocompleteuserwidget': {
                userSelected: this._onAddSelectedUser
            },
        });
        this.mon(this.getRelatedStudentsStore().proxy, {
            scope: this,
            exception: this._onRelatedStoreProxyError
        });
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        this.period_id = this.getOverview().period_id;
        this._loadPeriod(this.period_id);
        this._loadRelatedStudents(this.period_id);
    },

    _resetToHelpView: function() {
        this.getSidebarDeck().getLayout().setActiveItem('helpBox');
    },

    //
    //
    // Load related
    //
    //
    _loadRelatedStudents: function(period_id) {
        this.getRelatedStudentsStore().loadInPeriod(period_id, {
            scope: this,
            callback: this._onLoadRelatedStudents
        });
    },

    _onLoadRelatedStudents: function(records, operation) {
        if(operation.success) {
            this._onLoadRelatedStudentsSuccess(records);
        } else {
            // NOTE: Errors is handled by _onRelatedStoreProxyError
        }
    },
    _onLoadRelatedStudentsSuccess: function(records) {
        //console.log(records);
    },

    //
    //
    // Load period
    //
    //

    _loadPeriod: function(period_id) {
        this.getPeriodModel().load(period_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this._onLoadPeriodSuccess(record);
                } else {
                    this._onLoadPeriodFailure(operation);
                }
            }
        });
    },
    _onLoadPeriodSuccess: function(record) {
        this.periodRecord = record;
        var path = this.getPathFromBreadcrumb(this.periodRecord);
        var label = gettext('Manage students');
        this.application.setTitle(Ext.String.format('{0} - {1}', label, path));
        this.setSubviewBreadcrumb(this.periodRecord, 'Period', [], label);
    },
    _onLoadPeriodFailure: function(operation) {
        this.onLoadFailure(operation);
    },


    //
    //
    // Proxy success/error
    //
    //
    _onRelatedStoreProxyError: function(proxy, response, operation) {
        this.handleProxyErrorNoForm(this.getGlobalAlertmessagelist(), response, operation);
    },

    _onSyncSuccess: function(message) {
        this.getGrid().setLoading(false);
        this.getGlobalAlertmessagelist().add({
            type: 'success',
            message: message,
            autoclose: true
        });
    },

    //
    //
    // Remove student(s)
    //
    //
    _onRemoveSelected: function() {
        var selModel = this.getGrid().getSelectionModel();
        var selectedRelatedUserRecords = selModel.getSelection();

        var names = [];
        Ext.Array.each(selectedRelatedUserRecords, function(relatedUserRecord) {
            var displayname = relatedUserRecord.getDisplayName();
            names.push(displayname);
        }, this);

        var store = this.getRelatedStudentsStore();
        store.remove(selectedRelatedUserRecords);
        this.getGrid().setLoading(gettext('Saving') + ' ...');
        store.sync({
            scope: this,
            success: function() {
                var msg = gettext('Removed: {0}');
                this._onSyncSuccess(Ext.String.format(msg, names.join(', ')));
            }
        });
    },

    
    //
    //
    // Add student
    //
    //

    _onGridAddButton: function() {
        this.getSidebarDeck().getLayout().setActiveItem('selectRelatedUserPanel');
        this.getAutocompleteUserWidget().setValue('');
        this.getAutocompleteUserWidget().focus();
    },

    _onAddSelectedUser: function(combo, userRecord) {
        this._resetToHelpView();
        var store = this.getRelatedStudentsStore();
        var matchingRelatedUser = store.getByUserid(userRecord.get('id'));
        if(matchingRelatedUser === null) {
            var record = store.add({
                period: this.periodRecord.get('id'),
                user: userRecord.data
            })[0];
            store.sync({
                scope: this,
                success: function() {
                    this._onAddUserSuccess(record);
                }
            });
        } else {
            this.getGlobalAlertmessagelist().add({
                type: 'warning',
                message: Ext.String.format(gettext('{0} is already in the table.'),
                    matchingRelatedUser.getDisplayName()),
                autoclose: true
            });
        }
    },

    _onAddUserSuccess: function(relatedStudentRecord) {
        this._onSyncSuccess(Ext.String.format(gettext('{0} added.'),
            relatedStudentRecord.getDisplayName()));
        this.getGrid().getSelectionModel().select([relatedStudentRecord]);
    }
});
