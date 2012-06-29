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
        'loadAssignment': 'devilry_subjectadmin.utils.LoadAssignmentMixin'
    },

    requires: [
        'Ext.util.KeyMap'
    ],

    views: [
        'managestudents.Overview',
        'managestudents.ListOfGroups'
    ],

    /**
     * Get the related examiners store.
     * This store is automatically loaded with all the related examiners on the
     * period before the ``managestudentsSuccessfullyLoaded`` event is fired.
     * @return {devilry_subjectadmin.store.RelatedExaminers} Store.
     * @method getRelatedExaminersStore
     */

    /**
     * Get the related students store.
     * This store is automatically loaded with all the related students on the
     * period before the ``managestudentsSuccessfullyLoaded`` event is fired.
     * @return {devilry_subjectadmin.store.RelatedStudents} Store.
     * @method getRelatedStudentsStore
     */

    /**
     * Get the groups store.
     * This store is automatically loaded with all the groups on the assignment
     * before the ``managestudentsSuccessfullyLoaded`` event is fired.
     * @return {devilry_subjectadmin.store.Groups} Store.
     * @method getGroupsStore
     */

    stores: [
        'RelatedStudents',
        'RelatedExaminers',
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
                render: this._onRender
            },
            'viewport managestudentsoverview listofgroups': {
                selectionchange: this._onGroupSelectionChange,
                render: this._onRenderListOfGroups
            },
            'viewport managestudentsoverview #selectall': {
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

    _onRender: function() {
        this.assignment_id = this.getOverview().assignment_id;
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

    _cmp: function(x, y) {
        return x > y? 1 : x < y ? -1 : 0;
    },

    _sortByUsername: function(a, b) {
        this._sortByListProperty('students', 'student__username', a, b);
    },

    _sortByFullname: function(a, b) {
        this._sortByListProperty('students', 'student__devilryuserprofile__full_name', a, b);
    },

    _sortByListProperty: function(listproperty, attribute, a, b) {
        var listA = a.get(listproperty);
        var listB = b.get(listproperty);
        if(listA.length == 0) {
            return -1;
        }
        if(listB.length == 0) {
            return 1;
        }
        return this._cmp(listA[0][attribute], listB[0][attribute]);
    },

    _getLastname: function(fullname) {
        var split = fullname.split(/\s+/);
        return split[split.length-1];
    },

    _sortByLastname: function(a, b) {
        var listA = a.get('students');
        var listB = b.get('students');
        if(listA.length == 0) {
            return -1;
        }
        if(listB.length == 0) {
            return 1;
        }
        var attribute = 'student__devilryuserprofile__full_name';
        return this._cmp(
            this._getLastname(listA[0][attribute]),
            this._getLastname(listB[0][attribute])
        );
    },

    _onSelectAll: function() {
        this.getListOfGroups().getSelectionModel().selectAll();
    },

    setupProxies: function(periodid, assignmentid) {
        this.getGroupsStore().loadGroupsInAssignment(assignmentid);
        this.getRelatedStudentsStore().proxy.extraParams.periodid = periodid;
        this.getRelatedExaminersStore().proxy.extraParams.periodid = periodid;
    },

    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        //console.log('Assignment:', record.data);
        this._loadUserStores();
    },
    onLoadAssignmentFailure: function(operation) {
        console.log('ASSIGNMENT LOAD FAILED', operation);
    },

    /**
     * @private
     *
     * Load RelatedStudents and Groups stores.
     * */
    _loadUserStores: function() {
        this.setupProxies(
            this.assignmentRecord.get('parentnode'),
            this.assignmentRecord.get('id')
        );
        this.getOverview().setLoading(true);
        this._tmp_loadedStores = {
            total: 0,
            successful: 0,
            failed: 0
        }
        var loadConfig = {
            scope: this,
            callback: this._onUserStoreLoaded
        };
        this.getGroupsStore().load(loadConfig);
        this.getRelatedStudentsStore().load(loadConfig);
        this.getRelatedExaminersStore().load(loadConfig);
    },

    /**
     * @private
     *
     * Called for each of the user stores, and calls _onAllUserStoresLoaded
     * when all of them are finished loading.
     */
    _onUserStoreLoaded: function(records, operation) {
        this._tmp_loadedStores.total ++;
        if(operation.success) {
            this._tmp_loadedStores.successful ++;
        } else {
            this._tmp_loadedStores.failed ++;
        }
        var all_loaded = this._tmp_loadedStores.total == 3; // Groups, RelatedStudents, RelatedExaminers
        if(all_loaded && this._tmp_loadedStores.failed == 0) { 
            this._onAllUserStoresLoaded();
        } else {
            this.getOverview().setLoading(false);
            var errormsg = gettext('Failed to load parts of the page. Please try to reload the page.');
            Ext.Msg.show({
                title: 'Error',
                msg: errormsg,
                icon: Ext.Msg.ERROR
            });
        }
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

    _onAllUserStoresLoaded: function() {
        this.getOverview().setLoading(false);
        this.getOverview().addClass('devilry_subjectadmin_all_items_loaded'); // Mostly for the selenium tests, however someone may do something with it in a theme
        this.application.fireEvent('managestudentsSuccessfullyLoaded', this);
        this._handleNoGroupsSelected();
    },

    _onGroupSelectionChange: function(gridSelectionModel, selectedGroupRecords) {
        if(selectedGroupRecords.length === 1) {
            this._handleSingleGroupSelected(selectedGroupRecords[0]);
        } else if(selectedGroupRecords.length > 1) {
            this._handleMultipleGroupsSelected(selectedGroupRecords);
        } else {
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
    }
});
