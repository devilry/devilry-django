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

    stores: [
        'RelatedStudentsRo',
        'RelatedExaminersRo',
        'SearchForGroups',
        'Groups'
    ],

    models: ['Assignment'],


    /**
     * Get the main view for managestudents.
     * @return {devilry_subjectadmin.view.managestudents.Overview} The overview.
     * @method getOverview
     */

    /**
     * Get the toolbar for list of groups. Useful if a plugin needs to add
     * items to this toolbar.
     * @return {Ext.toolbar.Toolbar} The toolbar.
     * @method getPrimaryToolbar
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
    }, {
        ref: 'primaryToolbar',
        selector: 'managestudentsoverview #primaryToolbar'
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
            'viewport managestudentsoverview #sortby': {
                select: this._onSelectSortBy
            },
            'viewport managestudentsoverview #viewselect': {
                select: this._onSelectViewSelect
            },
            'viewport managestudentsoverview #search': {
                change: this._onSearchChange
            }
        });
    },

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
        this._sortBy('fullname'); // NOTE: This must match the field selected as value for the sortby in the view.
    },

    _onSearchChange: function(field, newValue, oldValue) {
        alert('Search is not supported yet');
    },

    _onSelectViewSelect: function(combo, records) {
        var view = records[0].get('value');
        this._view(view);
    },

    _view: function(view) {
        alert('Not implemented');
    },

    _onSelectSortBy: function(combo, records) {
        var sortby = records[0].get('value');
        this._sortBy(sortby);
    },

    _sortBy: function(sortby) {
        var sorter = null;
        if(sortby == 'username') {
            sorter = this._sortByUsername;
        } else if(sortby == 'fullname') {
            sorter = this._sortByFullname;
        } else if(sortby == 'lastname') {
            sorter = this._sortByLastname;
        } else {
            throw "Invalid sorter: " + sortby;
        }
        this.getGroupsStore().sort(Ext.create('Ext.util.Sorter', {
            sorterFn: Ext.bind(sorter, this)
        }));
    },

    _sortByUsername: function(a, b) {
        return this._sortByUserlisProperty('candidates', 'username', a, b);
    },

    _sortByFullname: function(a, b) {
        return this._sortByUserlisProperty('candidates', 'full_name', a, b);
    },

    _sortByUserlisProperty: function(listproperty, attribute, a, b) {
        var listA = a.get(listproperty);
        var listB = b.get(listproperty);
        if(listA.length == 0) {
            return -1;
        }
        if(listB.length == 0) {
            return 1;
        }
        var a = listA[0].user[attribute]
        var b = listB[0].user[attribute];
        return a.localeCompare(b);
    },

    _getLastname: function(fullname) {
        var split = fullname.split(/\s+/);
        return split[split.length-1];
    },

    _sortByLastname: function(a, b) {
        var listA = a.get('candidates');
        var listB = b.get('candidates');
        if(listA.length == 0) {
            return -1;
        }
        if(listB.length == 0) {
            return 1;
        }
        var attribute = 'full_name';
        var a = this._getLastname(listA[0].user[attribute]);
        var b = this._getLastname(listB[0].user[attribute]);
        return a.localeCompare(b);
    },

    _onSelectAll: function() {
        this.getListOfGroups().getSelectionModel().selectAll();
    },

    /** Select the given group records.
     * @param {[devilry_subjectadmin.model.Group]} [groupRecords] Group records array.
     * @param {Boolean} [keepExisting=false] True to retain existing selections
     * */
    selectGroupRecords: function(groupRecords, keepExisting) {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        selectionModel.select(groupRecords, keepExisting);
    },

    getRecordByGroupId: function(groupId) {
        var index = this.getGroupsStore().findExact('id', groupId);
        if(index == -1) {
            return undefined;
        }
        return this.getGroupsStore().getAt(index);
    },

    groupRecordIsSelected: function(groupRecord) {
        return this.getListOfGroups().getSelectionModel().isSelected(groupRecord);
    },

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

    /**
     * @private
     *
     * Load RelatedStudents and Groups stores.
     * */
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
    },

    /**
     * Set the body component (the center area of the borderlayout). Removes
     * all components in the body before adding the new component.
     */
    setBody: function(component) {
        this.getBody().removeAll();
        this.getBody().add(component);
    },

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
        Ext.callback(callbackconfig.success, callbackconfig.scope);
    },

    _onSyncFailure: function(batch, options) {
        this._unmaskListOfGroups();
        console.log('failure', batch, options);
    }
});
