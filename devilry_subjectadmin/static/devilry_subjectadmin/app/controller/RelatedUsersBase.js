/**
 * Base class for the controller for related students and examiners
 */
Ext.define('devilry_subjectadmin.controller.RelatedUsersBase', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    summaryTpl: gettext('Showing {visiblecount}/{totalcount}'),

    resetToHelpView: function() {
        this.getSidebarDeck().getLayout().setActiveItem('helpBox');
    },

    //
    //
    // Must be implemented in subclasses
    //
    //

    // NOTE: getOverview() must also be available (use ref)

    getRelatedUsersStore: function() {
        throw "Must be implemented in subclasses.";
    },

    getLabel: function() {
        throw "Must be implemented in subclasses.";
    },
    onPeriodLoaded: function(periodpath) {
        throw "Must be implemented in subclasses.";
    },

    onFilterChange: function(field, newValue) {
        if(Ext.isEmpty(this.task)) {
            this.task = new Ext.util.DelayedTask(this._filter, this, [field]);
        }
        this.task.delay(200);
    },

    _filter: function(field) {
        var value = field.getValue();
        var store = this.getGrid().getStore();
        store.filterBy(function(record) {
            return this.matchRelatedUser(record, value.toLocaleLowerCase());
        }, this);
        this.updateGridSummaryBox();
    },

    matchRelatedUser: function(record, lowercaseValue) {
        var full_name = record.get('user').full_name;
        if(Ext.isEmpty(full_name)) {
            full_name = gettext('Full name missing');
        }
        var tags = record.get('tags');
        if(Ext.isEmpty(tags)) {
            tags = '';
        }
        return record.get('user').username.toLocaleLowerCase().indexOf(lowercaseValue) !== -1 ||
            full_name.toLocaleLowerCase().indexOf(lowercaseValue) !== -1 ||
            tags.toLocaleLowerCase().indexOf(lowercaseValue) !== -1;
    },

    updateGridSummaryBox: function() {
        var store = this.getGrid().getStore();
        this.getGridSummaryBox().update(Ext.create('Ext.XTemplate', this.summaryTpl).apply({
            totalcount: store.getTotalCount(),
            visiblecount: store.getCount()
        }));
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
        var label = this.getLabel();
        this.application.setTitle(Ext.String.format('{0} - {1}', label, path));
        this.setSubviewBreadcrumb(this.periodRecord, 'Period', [], label);
        this.onPeriodLoaded(path);
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
        //this._onProxyError(response, operation);
        // NOTE: We already do this in controller.period.Overview, so adding it here would result in duplicated error messages.
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
        var msg = gettext('Tagged %(users)s with: %(tags)s');
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
                var msg = gettext('Cleared tags on %(users)s.');
                this.showSyncSuccessMessage(interpolate(msg, {
                    users: names.join(', ')
                }, true));
            }
        });
    }
});
