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
        selector: 'viewport relatedstudents alertmessagelist#globalAlertmessagelist'
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
            this._onLoadRelatedStudentsFailure(operation);
        }
    },
    _onLoadRelatedStudentsSuccess: function(records) {
        console.log(records);
    },
    _onLoadRelatedStudentsFailure: function(operation) {
        this.onLoadFailure(operation);
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
        this.handleProxyUsingHtmlErrorDialog(response, operation);
    },

    _onSyncSuccess: function() {
        this.getGrid().setLoading(false);
    },

    //
    //
    // Remove student(s)
    //
    //
    _onRemoveSelected: function() {
        var selModel = this.getGrid().getSelectionModel();
        var selected = selModel.getSelection();
        var store = this.getRelatedStudentsStore();
        store.remove(selected);
        this.getGrid().setLoading(gettext('Saving') + ' ...');
        store.sync({
            scope: this,
            success: this._onSyncSuccess
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
            Ext.MessageBox.alert(gettext('Error'),
                gettext('User is already registered as related.'));
        }
    },

    _onAddUserSuccess: function(record) {
        this._onSyncSuccess();
        this.getGrid().getSelectionModel().select([record]);
    }
});
