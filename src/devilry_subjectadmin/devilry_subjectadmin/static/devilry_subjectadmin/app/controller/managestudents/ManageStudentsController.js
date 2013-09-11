/**
 * Controller for the managestudents overview.
 *
 * Provides loading of stores required for student management, and leaves everything else 
 * to plugins. The plugins get a reference to this controller from the
 * {@link devilry_subjectadmin.Application#managestudentsSuccessfullyLoaded} event, and
 * they use the documented methods to hook themselves into the user interface.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.ManageStudentsController', {
    extend: 'Ext.app.Controller',

    mixins: {
        'loadAssignment': 'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'setBreadcrumb': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin'
    },

    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.HtmlErrorDialog',
        'devilry_extjsextras.ConfirmDeleteDialog',
        'Ext.util.DelayedTask'
    ],

    views: [
        'managestudents.ManageStudentsOverview',
        'managestudents.ListOfGroups'
    ],

    /**
     * Get the related examiners store.
     * @return {devilry_subjectadmin.store.RelatedExaminers} Store.
     * @method getRelatedExaminersRoStore
     */

    /**
     * Get the related students store.
     * @return {devilry_subjectadmin.store.RelatedStudents} Store.
     * @method getRelatedStudentsRoStore
     */

    /**
     * Get the search for groups store.
     * @return {devilry_subjectadmin.store.RelatedStudents} Store.
     * @method getSearchForGroupsStore
     */

    /**
     * Get the groups store.
     * This store is automatically loaded with all the groups on the assignment
     * before the ``managestudentsSuccessfullyLoaded`` event is fired.
     * @return {devilry_subjectadmin.store.Groups} Store.
     * @method getGroupsStore
     */


    /**
     * @property {Object} [assignmentRecord]
     * The assignment record. Loaded before any group records are loaded, which
     * means that it is available in the selection handlers.
     */


    listofgroups_size_cookiename: 'devilry_subjectadmin.managestudents.ListOfGroups.width',

    stores: [
        'RelatedStudentsRo',
        'RelatedExaminersRo',
        'SearchForGroups',
        'Groups'
    ],

    models: ['Assignment'],

    defaultGroupsSorter: 'fullname',


    /**
     * Get the main view for managestudents.
     * @return {devilry_subjectadmin.view.managestudents.Overview} The overview.
     * @method getOverview
     */

    refs: [{
        ref: 'overview',
        selector: 'managestudentsoverview'
    }, {
        ref: 'viewport',
        selector: 'viewport'
    }, {
        ref: 'listOfGroups',
        selector: 'listofgroups'
    }, {
        ref: 'body',
        selector: 'managestudentsoverview #body'
    }],

    init: function() {
        this.control({
            'viewport managestudentsoverview #addstudents': {
                click: this._onAddstudents
            },
            'viewport managestudentsoverview': {
                render: this._onRenderOverview
            },
            'viewport managestudentsoverview listofgroups': {
                selectionchange: this._onGroupSelectionChange,
                render: this._onRenderListOfGroups,
                resize: this._onListOfGroupsResize,
                boxready: this._onListOfGroupsBoxReady
            },
            'viewport managestudentsoverview sortgroupsbybutton': {
                afterSortBy: this._onAfterSortBy
            }
        });
    },

    getTotalGroupsCount: function() {
        return this.getGroupsStore().count();
    },


    _onAddstudents: function() {
        this.application.route.navigate(devilry_subjectadmin.utils.UrlLookup.manageStudentsAddStudents(this.assignmentRecord.get('id')));
    },


    /*****************************************************
     *
     * Render handlers
     *
     *****************************************************/

    _onRenderOverview: function() {
        this.assignment_id = this.getOverview().assignment_id;
        Ext.defer(function() { // Hack to work around the problem of the entire panel not completely loaded, which makes the loadmask render wrong
            if(this.assignmentRecord === undefined) {
                this.getOverview().setLoading(gettext('Loading') + ' ...');
            }
        }, 100, this);
        this.setLoadingBreadcrumb();
        this.loadAssignment(this.assignment_id);
    },

    _onRenderListOfGroups: function() {
        this.getGroupsStore().sortBySpecialSorter(this.getCurrentGroupsStoreSorter());
    },



    /*************************************
     * List of groups resize
     *************************************/
    _onListOfGroupsResize: function(listofgroups, width, height, oldWidth, oldHeight) {
        var maxWidth = this.getViewport().getWidth() - 200;
        if(width > maxWidth) { // Limit the maxwidth - this is only to avoid that the resizer loads or are pulled out of sight, and not to ensure proper and pretty layout.
            listofgroups.setWidth(maxWidth);
        } else {
            var firstLoad = Ext.isEmpty(oldWidth);
            if(!firstLoad) {
                Ext.util.Cookies.set(this.listofgroups_size_cookiename, width);
            }
        }
    },
    _onListOfGroupsBoxReady: function(listofgroups) {
        var width = Ext.util.Cookies.get(this.listofgroups_size_cookiename);
        if(width) {
            listofgroups.setWidth(parseInt(width, 10));
        }
    },





    /****************************************
     *
     * Select view
     *
     ****************************************/


    //_onSelectViewSelect: function(combo, records) {
        //var groupby = records[0].get('value');
        //this._groupby(groupby);
    //},

    //_groupby: function(groupby) {
        //console.log('Group by', groupby);
        //if(groupby == 'flat') {
            //this.getGroupsStore().clearGrouping();
        //} else {
            //this.getGroupsStore().groupBySpecialGrouper(groupby);
            ////Ext.defer(function() {
                ////console.log('Groups', this.getGroupsStore().getGroups());
                ////this.getListOfGroups().groupingFeature.collapseAll();
            ////}, 500, this);
        //}
    //},





    /****************************************
     *
     * Sort by
     *
     ****************************************/

    _onAfterSortBy: function(sorter) {
        this.currentGroupsStoreSorter = sorter;
        this.application.fireEvent('managestudentsGroupSorterChanged', this.currentGroupsStoreSorter);
    },

    getCurrentGroupsStoreSorter: function() {
        return this.currentGroupsStoreSorter || this.defaultGroupsSorter;
    },



    /***************************************************
     *
     * Methods to simplify selecting users
     *
     **************************************************/


    /** Select the given group records.
     * @param {[devilry_subjectadmin.model.Group]} [groupRecords] Group records array.
     * @param {Boolean} [keepExisting=false] True to retain existing selections
     * */
    _selectGroupRecords: function(groupRecords, keepExisting) {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        selectionModel.select(groupRecords, keepExisting);
    },

    _selectByGroupIds: function(groupIds) {
        var groupsStore = this.getGroupsStore();
        var selectedGroups = [];
        Ext.Array.each(groupIds, function(id) {
            var index = groupsStore.findExact('id', id);
            if(index != -1) {
                var record = groupsStore.getAt(index);
                selectedGroups.push(record);
            }
        }, this);
        this._selectGroupRecords(selectedGroups);
    },


    /*********************************************
     *
     * Handle selection change
     *
     *********************************************/

    _setSelectionUrl: function(selectedGroupRecords) {
        var select_delivery_on_load = !Ext.isEmpty(this.getOverview().select_delivery_on_load);
        // NOTE: We do not change hash if ``select_delivery_on_load``, since the hash should already be correct
        if(!select_delivery_on_load) {
            var group_ids = [];
            Ext.Array.each(selectedGroupRecords, function(record) {
                group_ids.push(record.get('id'));
            }, this);
            var assignment_id = this.assignmentRecord.get('id');
            var hash = devilry_subjectadmin.utils.UrlLookup.manageSpecificGroups(assignment_id, group_ids);
            this.application.route.setHashWithoutEvent(hash);
        }
    },

    _onGroupSelectionChange: function(gridSelectionModel, selectedGroupRecords) {
        if(!Ext.isEmpty(this.selectiontask)) {
            //this.getBody().setLoading(false);
            this.selectiontask.cancel();
        }
        //this.getBody().setLoading(true);
        this.selectiontask = new Ext.util.DelayedTask(function() {
            //this.getBody().setLoading(false);
            this._changeSelection(gridSelectionModel, selectedGroupRecords);
        }, this);
        this.selectiontask.delay(50);
    },

    _changeSelection: function(gridSelectionModel, selectedGroupRecords) {
        if(selectedGroupRecords.length > 0) {
            this._deselectAborted = true;
            this._setSelectionUrl(selectedGroupRecords);
            if(selectedGroupRecords.length === 1) {
                this._handleSingleGroupSelected(selectedGroupRecords[0]);
            } else {
                this._handleMultipleGroupsSelected(selectedGroupRecords);
            }
        } else {
            this._setSelectionUrl([]);
            this._handleNoGroupsSelected();
        }
    },

    _handleNoGroupsSelected: function() {
        this.application.fireEvent('managestudentsNoGroupSelected', this);
    },

    _handleSingleGroupSelected: function(groupRecord) {
        this.application.fireEvent('managestudentsSingleGroupSelected', this, groupRecord);
    },

    _handleMultipleGroupsSelected: function(groupRecords) {
        this.application.fireEvent('managestudentsMultipleGroupsSelected', this, groupRecords);
    },


    setBodyCard: function(itemId) {
        this.getBody().getLayout().setActiveItem(itemId);
    },




    /********************************************************
     *
     * Select by IDs in the URL
     *
     ********************************************************/

    _selectUrlIds: function() {
        var select_groupids_on_load = this.getOverview().select_groupids_on_load;
        if(!select_groupids_on_load) {
            this._handleNoGroupsSelected();
            return;
        }
        var groupIds = [];
        Ext.Array.each(select_groupids_on_load.split(','), function(strid) {
            var id = parseInt(strid, 10);
            groupIds.push(id);
        }, this);
        this._selectByGroupIds(groupIds);
    },



    /***************************************************
     *
     * Load stores
     *
     ***************************************************/

    _handleLoadError: function(operation, title) {
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        error.addErrors(null, operation);
        var errormessage = error.asHtmlList();
        Ext.widget('htmlerrordialog', {
            title: title,
            bodyHtml: errormessage
        }).show();
    },

    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        var period_id = this.assignmentRecord.get('parentnode');
        this.getRelatedExaminersRoStore().setAssignment(this.assignmentRecord.get('id'));
        this.getRelatedStudentsRoStore().setAssignment(this.assignmentRecord.get('id'));
        this.getSearchForGroupsStore().setAssignment(this.assignmentRecord.get('id'));
        this.getOverview().setLoading(false);
        this._loadGroupsStore();
        this.getRelatedExaminersRoStore().load();
    },
    onLoadAssignmentFailure: function(operation) {
        this.getOverview().setLoading(false);
        this._handleLoadError(operation, gettext('Failed to load assignment'));
    },

    _loadGroupsStore: function(groupIdsToSelectOnLoad) {
        this.getOverview().setLoading(gettext('Loading') + ' ...');
        this.getGroupsStore().loadGroupsInAssignment(this.assignmentRecord.get('id'), {
            scope: this,
            callback: function(records, operation) {
                this.getOverview().setLoading(false);
                if(operation.success) {
                    this._onLoadGroupsStoreSuccess(groupIdsToSelectOnLoad);
                } else {
                    this._handleLoadError(operation, gettext('Failed to load groups'));
                }
            }
        });
    },
    _onLoadGroupsStoreSuccess: function(groupIdsToSelectOnLoad) {
        this.getOverview().setLoading(false);
        this.getOverview().addClass('devilry_subjectadmin_all_items_loaded'); // Mostly for the selenium tests, however someone may do something with it in a theme
        this.application.fireEvent('managestudentsSuccessfullyLoaded', this);
        this._setBreadcrumbAndTitle();
        if(groupIdsToSelectOnLoad) {
            this._selectByGroupIds(groupIdsToSelectOnLoad);
        } else {
            this._selectUrlIds();
        }
    },

    _setBreadcrumbAndTitle: function() {
        var text = gettext('Students');
        this.setSubviewBreadcrumb(this.assignmentRecord, 'Assignment', [], text);
        var path = this.getPathFromBreadcrumb(this.assignmentRecord);
        this.application.setTitle(Ext.String.format('{0}.{1}', path, text));
    },





    /***************************************************
     *
     * Sync Groups store
     *
     ***************************************************/


    _maskListOfGroups: function(message) {
        message = message || gettext('Saving') + ' ...';
        this.getListOfGroups().setLoading(message);
    },

    _unmaskListOfGroups: function() {
        this.getListOfGroups().setLoading(false);
    },

    /** Used by related controllers (MultipleGroupsSelectedViewPlugin) to
     * notify this controller when multiple groups have changed, and needs to
     * be saved. */
    notifyMultipleGroupsChange: function(callbackconfig, apiOptions) {
        this._notifyGroupsChange(callbackconfig, false, apiOptions);
    },

    /** Used by related controllers (SingleGroupSelectedViewPlugin) to notify this
     * controller when a single group is changed, and needs to be saved. */
    notifySingleGroupChange: function(callbackconfig) {
        this._notifyGroupsChange(callbackconfig);
    },

    /** Used by related controllers (SingleGroupSelectedViewPlugin,
     * MultipleGroupsSelectedViewPlugin) to remove groups. */
    removeGroups: function(groupRecords) {
        var groups = devilry_subjectadmin.model.Group.formatIdentsAsStringList(groupRecords);
        Ext.create('devilry_extjsextras.ConfirmDeleteDialog', {
            short_description: Ext.String.ellipsis(groups, 100),
            width: 450,
            height: 330,
            listeners: {
                scope: this,
                deleteConfirmed: function(win) {
                    win.close();
                    this._removeGroups(groupRecords);
                }
            }
        }).show();
    },

    _removeGroups: function(groupRecords) {
        this.getGroupsStore().suspendEvents(); // Suspend events to avoid that we re-draw and re-select for each removal
        this.getGroupsStore().remove(groupRecords);
        this.getGroupsStore().resumeEvents();
        this._notifyGroupsChange({
            scope: this,
            success: function() {
                var groups = devilry_subjectadmin.model.Group.formatIdentsAsStringList(groupRecords);
                this.application.getAlertmessagelist().add({
                    message: Ext.String.format(gettext('Removed: {0}.'), groups),
                    type: 'success',
                    autoclose: true
                });
                this.reloadGroups([]); // Reload groups, since we suspended events above
            }
        }, true); // reloadOnError=true
    },

    _notifyGroupsChange: function(callbackconfig, reloadOnError, apiOptions) {
        this._maskListOfGroups();
        if(Ext.isEmpty(apiOptions)) {
            apiOptions = {};
        }
        this.getGroupsStore().setApiOptions(apiOptions);
        this.getGroupsStore().sync({
            scope: this,
            success: function(batch, options) {
                this._onSyncSuccess(batch, options, callbackconfig);
            },
            failure: function(batch, options) {
                this._onSyncFailure(batch, options, reloadOnError);
            }
        });
    },

    _onSyncSuccess: function(batch, options, callbackconfig) {
        this._unmaskListOfGroups();
        var affectedRecords = [];
        var operations = batch.operations;
        Ext.Array.each(operations, function(operation) {
            if(operation.action == 'update' || operation.action == 'create') {
                Ext.Array.each(operation.records, function(record) {
                    affectedRecords.push(record);
                }, this);
            }
        }, this);
        this._selectGroupRecords(affectedRecords);
        if(callbackconfig) {
            Ext.callback(callbackconfig.success, callbackconfig.scope);
        }
    },

    _onSyncFailure: function(batch, options, reloadOnError) {
        this._unmaskListOfGroups();
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        error.addBatchErrors(batch);
        var messages = error.asArrayOfStrings();
        this.application.getAlertmessagelist().addMany(messages, 'error');
        if(reloadOnError) {
            this.reloadGroups([]);
        }
    },

    /** Used by plugins to reload groups.
     * @param groupIdsToSelectOnLoad Array of group IDs to select on load.
     * */
    reloadGroups: function(groupIdsToSelectOnLoad) {
        this._loadGroupsStore(groupIdsToSelectOnLoad);
    }
});
