/**
 * Controller for the related examiners view
 */
Ext.define('devilry_subjectadmin.controller.RelatedExaminers', {
    extend: 'devilry_subjectadmin.controller.RelatedUsersBase',

    views: [
        'relatedexaminers.Overview'
    ],

    stores: ['RelatedExaminers'],
    models: ['Period'],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
    }, {
        ref: 'overview',
        selector: 'viewport relatedexaminers'
    }, {
        ref: 'heading',
        selector: 'viewport relatedexaminers #heading'
    }, {
        ref: 'grid',
        selector: 'viewport relatedexaminers relatedexaminersgrid'
    }, {
        ref: 'gridSummaryBox',
        selector: 'viewport relatedexaminers #gridSummaryBox'
    }, {
        ref: 'addButton',
        selector: 'viewport relatedexaminers #addButton'
    }, {
        ref: 'removeButton',
        selector: 'viewport relatedexaminers #removeButton'
    }, {
        ref: 'tagsButton',
        selector: 'viewport relatedexaminers #tagsButton'
    }, {
        ref: 'sidebarDeck',
        selector: 'viewport relatedexaminers #sidebarDeck'
    }, {
        ref: 'autocompleteUserWidget',
        selector: 'viewport relatedexaminers autocompleteuserwidget'
    }],

    init: function() {
        // NOTE: All of the handlers not starting with ``_`` is inherited from RelatedUsersBase.
        this.control({
            'viewport relatedexaminers': {
                render: this._onRender
            },

            'viewport relatedexaminers relatedexaminersgrid': {
                selectionchange: this._onGridSelectionChange
            },

            'viewport relatedexaminers #filterfield': {
                change: this.onFilterChange // NOTE: Implemented in RelatedUsersBase
            },

            // Remove examiners
            'viewport relatedexaminers #removeButton': {
                click: this._onRemoveSelected
            },
            'viewport relatedexaminers okcancelpanel#confirmRemovePanel': {
                cancel: this.resetToHelpView,
                ok: this._removeSelected
            },


            // setTags
            'viewport relatedexaminers #setTagsButton': {
                click: this.onSetTagsClick
            },
            'viewport relatedexaminers choosetagspanel#setTagsPanel': {
                cancel: this.resetToHelpView,
                savetags: this.onSetTagsSave
            },

            // addTags
            'viewport relatedexaminers #addTagsButton': {
                click: this.onAddTagsButtonClick
            },
            'viewport relatedexaminers choosetagspanel#addTagsPanel': {
                cancel: this.resetToHelpView,
                savetags: this.onAddTagsSave
            },

            // clearTags
            'viewport relatedexaminers #clearTagsButton': {
                click: this.onClearTagsClick
            },
            'viewport relatedexaminers okcancelpanel#clearTagsPanel': {
                cancel: this.resetToHelpView,
                ok: this.onClearTagsConfirmed
            },


            // Add examiner
            'viewport relatedexaminers #addButton': {
                click: this._onAddUserButtonClick
            },
            'viewport relatedexaminers selectrelateduserpanel': {
                cancel: this.resetToHelpView
            },
            'viewport relatedexaminers selectrelateduserpanel autocompleteuserwidget': {
                userSelected: this._onAddSelectedUser
            }
        });

        this.mon(this.getRelatedExaminersStore().proxy, {
            scope: this,
            exception: this.onRelatedStoreProxyError
        });
        this.mon(this.getPeriodModel().proxy, {
            scope: this,
            exception: this.onPeriodProxyError
        });
    },

    getRelatedUsersStore: function() {
        return this.getRelatedExaminersStore();
    },
    getLabel: function() {
        return gettext('Examiners');
    },
    onPeriodLoaded: function(periodpath) {
        this.getHeading().update({
            periodpath: periodpath
        });
    },

    _onRender: function() {
        var period_id = this.getOverview().period_id;
        this.loadPeriod(period_id);
        this._loadRelatedExaminers(period_id);
    },


    //
    //
    // Load related
    //
    //
    _loadRelatedExaminers: function(period_id) {
        this.getRelatedExaminersStore().loadInPeriod(period_id, {
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadRelatedStudentsSuccess();
                }
            }
        });
    },
    _onLoadRelatedStudentsSuccess: function() {
        this.updateGridSummaryBox();
    },


    //
    //
    // Grid
    //
    //
    _onGridSelectionChange: function(selModel, selected) {
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
    // Remove examiner(s)
    //
    //
    _onRemoveSelected: function() {
        this.getSidebarDeck().getLayout().setActiveItem('confirmRemovePanel');
    },


    _removeSelected: function() {
        this.resetToHelpView();
        var selectedRelatedUserRecords = this._getSelectedRelatedUserRecords();
        var names = devilry_subjectadmin.model.RelatedUserBase.recordsAsDisplaynameArray(selectedRelatedUserRecords);

        var store = this.getRelatedExaminersStore();
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
    // Add examiner
    //
    //

    _onAddUserButtonClick: function() {
        this.getSidebarDeck().getLayout().setActiveItem('selectRelatedUserPanel');
        this.getAutocompleteUserWidget().setValue('');
        this.getAutocompleteUserWidget().focus();
    },

    _onAddSelectedUser: function(combo, userRecord) {
        this.resetToHelpView();
        var store = this.getRelatedExaminersStore();
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
        this.getAddButton().focus(false, 200);
    },

    _onAddUserSuccess: function(relatedExaminerRecord) {
        this.showSyncSuccessMessage(Ext.String.format(gettext('{0} added.'),
            relatedExaminerRecord.getDisplayName()));
        this.getGrid().getSelectionModel().select([relatedExaminerRecord]);
    }
});
