/**
 * Controller for the related students view
 */
Ext.define('devilry_subjectadmin.controller.RelatedStudents', {
    extend: 'devilry_subjectadmin.controller.RelatedUsersBase',

    views: [
        'relatedstudents.Overview'
    ],

    stores: ['RelatedStudents'],
    models: ['Period'],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
    }, {
        ref: 'overview',
        selector: 'viewport relatedstudents'
    }, {
        ref: 'grid',
        selector: 'viewport relatedstudents relatedstudentsgrid'
    }, {
        ref: 'removeButton',
        selector: 'viewport relatedstudents #removeButton'
    }, {
        ref: 'tagsButton',
        selector: 'viewport relatedstudents #tagsButton'
    }, {
        ref: 'sidebarDeck',
        selector: 'viewport relatedstudents #sidebarDeck'
    }, {
        ref: 'autocompleteUserWidget',
        selector: 'viewport relatedstudents autocompleteuserwidget'
    }],

    init: function() {
        // NOTE: All of the handlers not starting with ``_`` is inherited from RelatedUsersBase.
        this.control({
            'viewport relatedstudents': {
                render: this._onRender
            },

            'viewport relatedstudents relatedstudentsgrid': {
                selectionchange: this._onGridSelectionChange
            },

            // Remove students
            'viewport relatedstudents #removeButton': {
                click: this._onRemoveSelected
            },
            'viewport relatedstudents okcancelpanel#confirmRemovePanel': {
                cancel: this.resetToHelpView,
                ok: this._removeSelected
            },


            // setTags
            'viewport relatedstudents #setTagsButton': {
                click: this.onSetTagsClick
            },
            'viewport relatedstudents choosetagspanel#setTagsPanel': {
                cancel: this.resetToHelpView,
                savetags: this.onSetTagsSave
            },

            // addTags
            'viewport relatedstudents #addTagsButton': {
                click: this.onAddTagsButtonClick
            },
            'viewport relatedstudents choosetagspanel#addTagsPanel': {
                cancel: this.resetToHelpView,
                savetags: this.onAddTagsSave
            },

            // clearTags
            'viewport relatedstudents #clearTagsButton': {
                click: this.onClearTagsClick
            },
            'viewport relatedstudents okcancelpanel#clearTagsPanel': {
                cancel: this.resetToHelpView,
                ok: this.onClearTagsConfirmed
            },


            // Add student
            'viewport relatedstudents #addButton': {
                click: this._onAddUserButtonClick
            },
            'viewport relatedstudents selectrelateduserpanel': {
                cancel: this.resetToHelpView
            },
            'viewport relatedstudents selectrelateduserpanel autocompleteuserwidget': {
                userSelected: this._onAddSelectedUser
            },
        });

        this.mon(this.getRelatedStudentsStore().proxy, {
            scope: this,
            exception: this.onRelatedStoreProxyError
        });
        this.mon(this.getPeriodModel().proxy, {
            scope: this,
            exception: this.onPeriodProxyError
        });
    },

    _onRender: function() {
        var period_id = this.getOverview().period_id;
        this.loadPeriod(period_id);
        this._loadRelatedStudents(period_id);
    },


    //
    //
    // Load related
    //
    //
    _loadRelatedStudents: function(period_id) {
        this.getRelatedStudentsStore().loadInPeriod(period_id);
    },


    //
    //
    // Grid
    //
    //
    _onGridSelectionChange: function(grid, selected) {
        if(selected.length === 0) {
            this.getRemoveButton().disable();
            this.getTagsButton().disable();
        } else {
            this.getRemoveButton().enable();
            this.getTagsButton().enable();
        }
    },
    _getSelectedRelatedUserRecords: function() {
        var selModel = this.getGrid().getSelectionModel();
        var selectedRelatedUserRecords = selModel.getSelection();
        return selectedRelatedUserRecords;
    },


    //
    //
    // Remove student(s)
    //
    //
    _onRemoveSelected: function() {
        this.getSidebarDeck().getLayout().setActiveItem('confirmRemovePanel');
    },


    _removeSelected: function() {
        this.resetToHelpView();
        var selectedRelatedUserRecords = this._getSelectedRelatedUserRecords();
        var names = devilry_subjectadmin.model.RelatedUserBase.recordsAsDisplaynameArray(selectedRelatedUserRecords);

        var store = this.getRelatedStudentsStore();
        store.remove(selectedRelatedUserRecords);
        this.setLoading(gettext('Saving') + ' ...');
        store.sync({
            scope: this,
            success: function() {
                var msg = gettext('Removed: {0}');
                this.showSyncSuccessMessage(Ext.String.format(msg, names.join(', ')));
            }
        });
    },

    
    //
    //
    // Add student
    //
    //

    _onAddUserButtonClick: function() {
        this.getSidebarDeck().getLayout().setActiveItem('selectRelatedUserPanel');
        this.getAutocompleteUserWidget().setValue('');
        this.getAutocompleteUserWidget().focus();
    },

    _onAddSelectedUser: function(combo, userRecord) {
        this.resetToHelpView();
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
        this.showSyncSuccessMessage(Ext.String.format(gettext('{0} added.'),
            relatedStudentRecord.getDisplayName()));
        this.getGrid().getSelectionModel().select([relatedStudentRecord]);
    }
});
