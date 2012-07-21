/**
 * Controller for the managestudents overview.
 *
 * Provides loading of stores required for student management, and leaves everything else 
 * to plugins. The plugins get a reference to this controller from the
 * {@link devilry_subjectadmin.Application#managestudentsSuccessfullyLoaded} event, and
 * they use the documented methods to hook themselves into the user interface.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.Overview', {
    extend: 'Ext.app.Controller',

    mixins: {
        'loadAssignment': 'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'setBreadcrumb': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin'
    },

    requires: [
        'Ext.util.KeyMap',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.HtmlErrorDialog'
    ],

    views: [
        'managestudents.Overview',
        'managestudents.ListOfGroups',
        'managestudents.AutocompleteGroupWidget'
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
        ref: 'listOfGroups',
        selector: 'listofgroups'
    }, {
        ref: 'body',
        selector: 'managestudentsoverview #body'
    }],

    init: function() {
        this.control({
            'viewport managestudentsoverview': {
                render: this._onRenderOverview
            },
            'viewport managestudentsoverview listofgroups': {
                selectionchange: this._onGroupSelectionChange,
                render: this._onRenderListOfGroups
            },
            'viewport managestudentsoverview #selectButton #selectall': {
                click: this._onSelectAll
            },
            'viewport managestudentsoverview #selectButton #deselectall': {
                click: this._onDeselectAll
            },
            'viewport managestudentsoverview #selectButton #invertselection': {
                click: this._onInvertselection
            },
            'viewport managestudentsoverview #sortby': {
                select: this._onSelectSortBy
            },
            'viewport managestudentsoverview #viewselect': {
                select: this._onSelectViewSelect
            },
            'viewport #selectUsersByAutocompleteWidget': {
                userSelected: this._onUserSelectedBySearch
            }
        });
    },

    getTotalGroupsCount: function() {
        return this.getGroupsStore().count();
    },




    /*****************************************************
     *
     * Render handlers
     *
     *****************************************************/

    _onRenderOverview: function() {
        this.assignment_id = this.getOverview().assignment_id;
        Ext.defer(function() { // Hack to work around the problem of the entire panel not completely loaded, which makes the loadmask render wrong
            if(this.assignmentRecord == undefined) {
                this.getOverview().setLoading(gettext('Loading assignment ...'));
            }
        }, 100, this);
        this.loadAssignment(this.assignment_id);
    },

    _onRenderListOfGroups: function() {
        var map = new Ext.util.KeyMap(this.getListOfGroups().getEl(), {
            key: 'a',
            ctrl: true,
            fn: this._onSelectAll,
            scope: this
        });
        this.getGroupsStore().sortBySpecialSorter(this.getCurrentGroupsStoreSorter());
    },





    /****************************************
     *
     * Select view
     *
     ****************************************/


    _onSelectViewSelect: function(combo, records) {
        var view = records[0].get('value');
        this._view(view);
    },

    _view: function(view) {
        alert('Not implemented');
    },





    /****************************************
     *
     * Sort by
     *
     ****************************************/


    _onSelectSortBy: function(combo, records) {
        this.currentGroupsStoreSorter = records[0].get('value');
        this.getGroupsStore().sortBySpecialSorter(this.currentGroupsStoreSorter);
        this.application.fireEvent('managestudentsGroupSorterChanged', this.currentGroupsStoreSorter);
    },

    getCurrentGroupsStoreSorter: function() {
        return this.currentGroupsStoreSorter || this.defaultGroupsSorter;
    },



    /***********************************************
     *
     * Select menu button handlers
     *
     **********************************************/

    _onSelectAll: function() {
        this.getListOfGroups().getSelectionModel().selectAll();
    },
    _onDeselectAll: function() {
        this.getListOfGroups().getSelectionModel().deselectAll();
    },
    _onInvertselection: function() {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        var selected = Ext.clone(selectionModel.selected.items);

        // Add listener to the "next" selectionchange event, and trigger the selectionchange with selectAll
        this.getListOfGroups().on({
            selectionchange: function() {
                this.deselectGroupRecords(selected);
            },
            scope: this,
            single: true
        });
        this.getListOfGroups().getSelectionModel().selectAll();
    },



    /**************************************************
     *
     * Select by search
     *
     **************************************************/

    _showSelectSearchErrorMessage: function(combo, options) {
        Ext.MessageBox.show({
            title: options.title,
            msg: options.msg,
            buttons: Ext.MessageBox.OK,
            icon: Ext.MessageBox.ERROR,
            fn: function() {
                Ext.defer(function() {
                    combo.focus();
                }, 100);
            }
        });
    },

    _onUserSelectedBySearch: function(combo, searchGroupRecord) {
        // NOTE: This searchGroupRecord is not from the same proxy as the records in the
        //       "regular" list, so their internal IDs do not match. Therefore,
        //       we use getGroupRecordById() to get the correct receord.
        combo.clearValue();
        combo.focus();
        var groupId = searchGroupRecord.get('id');
        var groupRecord = this.getGroupRecordById(groupId);
        if(groupRecord) {
            if(this.groupRecordIsSelected(groupRecord)) {
                this._showSelectSearchErrorMessage(combo, {
                    title: gettext('Already selected'),
                    msg: gettext('The group is already selected')
                });
            } else {
                this.selectGroupRecords([groupRecord], true);
            }
        } else {
            this._showSelectSearchErrorMessage(combo, {
                title: gettext('Selected group not loaded'),
                msg: gettext('The group you selected is not loaded. This is probably because someone else added a group after you loaded this page. Try reloading the page.')
            });
        }
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
    selectGroupRecords: function(groupRecords, keepExisting) {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        selectionModel.select(groupRecords, keepExisting);
    },

    /** Deselect the given group records.
     * @param {[devilry_subjectadmin.model.Group]} [groupRecords] Group records array.
     * */
    deselectGroupRecords: function(groupRecords) {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        selectionModel.deselect(groupRecords);
    },

    /** Get group record by group id.
     * @param {int} [groupId] The group id.
     * @return {devilry_subjectadmin.model.Group} The group record, or ``undefined`` if it is not found.
     * */
    getGroupRecordById: function(groupId) {
        var index = this.getGroupsStore().findExact('id', groupId);
        if(index == -1) {
            return undefined;
        }
        return this.getGroupsStore().getAt(index);
    },

    /** Return ``true`` if ``groupRecord`` is selected. */
    groupRecordIsSelected: function(groupRecord) {
        return this.getListOfGroups().getSelectionModel().isSelected(groupRecord);
    },





    /*********************************************
     *
     * Handle selection change
     *
     *********************************************/

    _setSelectionUrl: function(selectedGroupRecords) {
        var ids = [];
        Ext.Array.each(selectedGroupRecords, function(record) {
            ids.push(record.get('id'));
        }, this);
        var hashpatt = '/assignment/{0}/@@manage-students/{1}';
        var hash = Ext.String.format(hashpatt, this.assignmentRecord.get('id'), ids.join(','));
        this.application.route.setHashWithoutEvent(hash);
    },

    _onGroupSelectionChange: function(gridSelectionModel, selectedGroupRecords) {
        if(selectedGroupRecords.length === 1) {
            this._handleSingleGroupSelected(selectedGroupRecords[0]);
            this._setSelectionUrl(selectedGroupRecords);
        } else if(selectedGroupRecords.length > 1) {
            this._handleMultipleGroupsSelected(selectedGroupRecords);
            this._setSelectionUrl(selectedGroupRecords);
        } else {
            this._handleNoGroupsSelected();
            this._setSelectionUrl([]);
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


    /**
     * Set the body component (the center area of the borderlayout). Removes
     * all components in the body before adding the new component.
     */
    setBody: function(component) {
        this.getBody().removeAll();
        this.getBody().add(component);
    },




    /********************************************************
     *
     * Select by IDs in the URL
     *
     ********************************************************/

    _selectUrlIds: function() {
        var selected_group_ids = this.getOverview().selected_group_ids;
        if(!selected_group_ids) {
            this._handleNoGroupsSelected();
            return;
        }
        var selectionModel = this.getListOfGroups().getSelectionModel();
        var groupsStore = this.getGroupsStore();
        var selectedGroups = [];
        Ext.Array.each(selected_group_ids.split(','), function(strid) {
            var id = parseInt(strid);
            var index = groupsStore.findExact('id', id);
            if(index != -1) {
                var record = groupsStore.getAt(index);
                selectedGroups.push(record);
            }
        }, this);
        this.selectGroupRecords(selectedGroups);
    },



    /***************************************************
     *
     * Load stores
     *
     ***************************************************/

    _handleLoadError: function(operation, title) {
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler', operation);
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
        this.getRelatedExaminersRoStore().setPeriod(period_id);
        this.getRelatedStudentsRoStore().setPeriod(period_id);
        this.getSearchForGroupsStore().setAssignment(this.assignmentRecord.get('id'));
        this.getOverview().setLoading(false);
        this._loadGroupsStore();
    },
    onLoadAssignmentFailure: function(operation) {
        this.getOverview().setLoading(false);
        this._handleLoadError(operation, gettext('Failed to load assignment'));
    },

    _loadGroupsStore: function() {
        this.getOverview().setLoading(gettext('Loading groups ...'));
        this.getGroupsStore().loadGroupsInAssignment(this.assignmentRecord.get('id'), {
            scope: this,
            callback: this._onLoadGroupsStore
        });
    },

    _onLoadGroupsStore: function(records, operation) {
        this.getOverview().setLoading(false);
        if(operation.success) {
            this._onLoadGroupsStoreSuccess();
        } else {
            this._handleLoadError(operation, gettext('Failed to load groups'));
        }
    },

    _onLoadGroupsStoreSuccess: function() {
        this.getOverview().setLoading(false);
        this.getOverview().addClass('devilry_subjectadmin_all_items_loaded'); // Mostly for the selenium tests, however someone may do something with it in a theme
        this.application.fireEvent('managestudentsSuccessfullyLoaded', this);
        this.setSubviewBreadcrumb(this.assignmentRecord, 'Assignment', [], gettext('Manage students'));
        this._selectUrlIds();
    },





    /***************************************************
     *
     * Sync Groups store
     *
     ***************************************************/


    _maskListOfGroups: function(message) {
        message = message || gettext('Saving ...');
        this.getListOfGroups().setLoading(message);
    },

    _unmaskListOfGroups: function() {
        this.getListOfGroups().setLoading(false);
    },

    /** Used by related controllers (MultipleGroupsSelectedViewPlugin) to
     * notify this controller when multiple groups have changed, and needs to
     * be saved. */
    notifyMultipleGroupsChange: function(callbackconfig) {
        this._notifyGroupsChange(callbackconfig);
    },

    /** Used by related controllers (SingleGroupSelectedViewPlugin) to notify this
     * controller when a single group is changed, and needs to be saved. */
    notifySingleGroupChange: function(callbackconfig) {
        this._notifyGroupsChange(callbackconfig);
    },

    _notifyGroupsChange: function(callbackconfig) {
        console.log('sync started');
        this._maskListOfGroups();
        this.getGroupsStore().sync({
            scope: this,
            success: function(batch, options) {
                this._onSyncSuccess(batch, options, callbackconfig);
            },
            failure: this._onSyncFailure
        });
    },

    _onSyncSuccess: function(batch, options, callbackconfig) {
        this._unmaskListOfGroups();
        console.log('sync success', batch);
        var affectedRecords = [];
        var operations = batch.operations;
        Ext.Array.each(operations, function(operation) {
            if(operation.action == 'update' || operation.action == 'create') {
                Ext.Array.each(operation.records, function(record) {
                    affectedRecords.push(record);
                }, this);
            }
        }, this);
        this.selectGroupRecords(affectedRecords);
        if(callbackconfig) {
            Ext.callback(callbackconfig.success, callbackconfig.scope);
        }
    },

    _onSyncFailure: function(batch, options) {
        this._unmaskListOfGroups();
        console.log('failure', batch, options);
    },






    /************************************************
     *
     * Other stuff
     *
     ************************************************/



    /**
     * Get the contents of the groups store (see {@link #getGroupsStore}
     * as an object with usernames as key and an array of
     * {@link devilry_subjectadmin.model.Group} records for values.
     *
     * The values are arrays because we support the same user in multiple
     * groups on the same assignment.
     */
    getGroupsMappedByUsername: function() {
        var map = {};
        this.getGroupsStore().each(function(record) {
            Ext.each(record.get('students'), function(student) {
                if(map[student.student__username]) {
                    map[student.student__username].push(record);
                } else {
                    map[student.student__username] = [record];
                }
            }, this);
        }, this);
        return map;
    },


    /**
     * Return ``true`` if this assignment is a project assignment.
     */
    isProjectAssignment: function() {
        return false;
    },

    /**
     * Get multiselect help message.
     */
    getMultiSelectHowto: function() {
        var shortcutkey = 'CTRL';
        if(Ext.isMac) {
            shortcutkey = 'CMD';
        }
        var tpl = Ext.create('Ext.XTemplate', gettext('Hold down <strong>{shortcutkey}</strong> to select more {groupunit_plural}.'));
        return tpl.apply({
            shortcutkey: shortcutkey,
            groupunit_plural: this.getTranslatedGroupUnit(true)
        });
    },

    /**
     * Get translated group unit string. E.g.: One of ``"student"`` or ``"group"``.
     * @param {boolean} pluralize Pluralize the group unit?
     */
    getTranslatedGroupUnit: function(pluralize) {
        var translatekey;
        var count = 0;
        if(pluralize) {
            count = 10;
        }
        if(this.isProjectAssignment()) {
            return npgettext('groupunit', 'project group', 'project groups', count);
        } else {
            return npgettext('groupunit', 'student', 'students', count);
        }
    }
});
