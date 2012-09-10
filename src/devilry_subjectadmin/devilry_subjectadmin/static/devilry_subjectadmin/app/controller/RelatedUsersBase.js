/**
 * Base class for the controller for related students and examiners
 */
Ext.define('devilry_subjectadmin.controller.RelatedUsersBase', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],


    resetToHelpView: function() {
        this.getSidebarDeck().getLayout().setActiveItem('helpBox');
    },


    getRelatedUsersStore: function() {
        throw "Must be implemented in subclasses.";
    },


    //
    //
    // Load period
    //
    //

    loadPeriod: function(period_id) {
        this.setLoadingBreadcrumb();
        this.getPeriodModel().load(period_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this._onLoadPeriodSuccess(record);
                } else {
                    // NOTE: Errors is handled in onPeriodProxyError
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
    _onProxyError: function(response, operation) {
        this.handleProxyErrorNoForm(this.getGlobalAlertmessagelist(), response, operation);
    },
    onRelatedStoreProxyError: function(proxy, response, operation) {
        this._onProxyError(response, operation);
    },
    onPeriodProxyError: function(proxy, response, operation) {
        this._onProxyError(response, operation);
    },


    showSyncSuccessMessage: function(message) {
        this.setLoading(false);
        this.getGlobalAlertmessagelist().add({
            type: 'success',
            message: message,
            autoclose: true
        });
    },

    
    setLoading: function(messageOrFalse) {
        this.getOverview().setLoading(messageOrFalse);
    },


    //
    //
    // Tags
    //
    //
    onTagSyncSuccess: function(selectedRelatedUserRecords, tagsArray) {
        this.resetToHelpView();
        var names = devilry_subjectadmin.model.RelatedUserBase.recordsAsDisplaynameArray(selectedRelatedUserRecords);
        var msg = gettext('Tagged %(users)s with: %(tags)s')
        this.showSyncSuccessMessage(interpolate(msg, {
            users: names.join(', '),
            tags: tagsArray.join(', ')
        }, true));
    },

    onSetTagsClick: function() {
        this.getSidebarDeck().getLayout().setActiveItem('setTagsPanel');
    },
    onSetTagsSave: function(panel, tagsArray) {
        var selectedRelatedUserRecords = this._getSelectedRelatedUserRecords();
        Ext.Array.each(selectedRelatedUserRecords, function(relatedUserRecord) {
            relatedUserRecord.setTagsFromArray(tagsArray);
        }, this);
        this.getRelatedUsersStore().sync({
            scope: this,
            success: function() {
                this.onTagSyncSuccess(selectedRelatedUserRecords, tagsArray);
            }
        });
    },

    onAddTagsButtonClick: function() {
        this.getSidebarDeck().getLayout().setActiveItem('addTagsPanel');
    },
    onAddTagsSave: function(panel, tagsArray) {
        var selectedRelatedUserRecords = this._getSelectedRelatedUserRecords();
        Ext.Array.each(selectedRelatedUserRecords, function(relatedUserRecord) {
            relatedUserRecord.addTagsFromArray(tagsArray);
        }, this);
        this.getRelatedUsersStore().sync({
            scope: this,
            success: function() {
                this.onTagSyncSuccess(selectedRelatedUserRecords, tagsArray);
            }
        });
    },

    onClearTagsClick: function() {
        this.getSidebarDeck().getLayout().setActiveItem('clearTagsPanel');
    },
    onClearTagsConfirmed: function() {
        var selectedRelatedUserRecords = this._getSelectedRelatedUserRecords();
        Ext.Array.each(selectedRelatedUserRecords, function(relatedUserRecord) {
            relatedUserRecord.clearTags();
        }, this);
        this.getRelatedUsersStore().sync({
            scope: this,
            success: function() {
                this.resetToHelpView();
                var names = devilry_subjectadmin.model.RelatedUserBase.recordsAsDisplaynameArray(selectedRelatedUserRecords);
                var msg = gettext('Cleared tags on %(users)s.')
                this.showSyncSuccessMessage(interpolate(msg, {
                    users: names.join(', ')
                }, true));
            }
        });
    }
});
