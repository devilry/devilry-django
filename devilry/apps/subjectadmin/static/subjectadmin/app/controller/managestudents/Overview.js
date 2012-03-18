/**
 * Controller for the managestudents overview.
 *
 * Provides loading of stores required for student management, and leaves everything else 
 * to plugins. The plugins get a reference to this controller from the
 * {@link subjectadmin.Application#managestudentsSuccessfullyLoaded} event, and
 * they use the documented methods to hook themselves into the user interface.
 */
Ext.define('subjectadmin.controller.managestudents.Overview', {
    extend: 'Ext.app.Controller',

    mixins: {
        'loadAssignment': 'subjectadmin.utils.LoadAssignmentMixin'
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
     * @return {subjectadmin.store.RelatedExaminers} Store.
     * @method getRelatedExaminersStore
     */

    /**
     * Get the related students store.
     * This store is automatically loaded with all the related students on the
     * period before the ``managestudentsSuccessfullyLoaded`` event is fired.
     * @return {subjectadmin.store.RelatedStudents} Store.
     * @method getRelatedStudentsStore
     */

    /**
     * Get the groups store.
     * This store is automatically loaded with all the groups on the assignment
     * before the ``managestudentsSuccessfullyLoaded`` event is fired.
     * @return {subjectadmin.store.Groups} Store.
     * @method getGroupsStore
     */

    stores: [
        'Assignments',
        'RelatedStudents',
        'RelatedExaminers',
        'Groups'
    ],


    /**
     * Get the main view for managestudents.
     * @return {subjectadmin.view.managestudents.Overview} The overview.
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
            }
        });
    },

    _onRender: function() {
        this.subject_shortname = this.getOverview().subject_shortname;
        this.period_shortname = this.getOverview().period_shortname;
        this.assignment_shortname = this.getOverview().assignment_shortname;
        //this.getOverview().getEl().mask(dtranslate('themebase.loading'));
        this.loadAssignment();
    },

    _onRenderListOfGroups: function() {
        var map = new Ext.util.KeyMap(this.getListOfGroups().getEl(), {
            key: 'a',
            ctrl: true,
            fn: this._onSelectAll,
            scope: this
        });
    },

    _onSelectAll: function() {
        this.getListOfGroups().getSelectionModel().selectAll();
    },

    /** Get the short name for the current subject. */
    getSubjectShortname: function() {
        return this.subject_shortname;
    },

    /** Get the short name for the current period. */
    getPeriodShortname: function() {
        return this.period_shortname;
    },

    /** Get the short name for the current assignment. */
    getAssignmentShortname: function() {
        return this.assignment_shortname;
    },

    setupProxies: function(periodid, assignmentid) {
        this.getGroupsStore().proxy.extraParams.assignmentid = assignmentid;
        this.getRelatedStudentsStore().proxy.extraParams.periodid = periodid;
        this.getRelatedExaminersStore().proxy.extraParams.periodid = periodid;
    },

    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        //console.log('Assignment:', record.data);
        this._loadUserStores();
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
        this.loadedStores = 0;
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
    _onUserStoreLoaded: function() {
        this.loadedStores ++;
        if(this.loadedStores == 3) { // Groups, RelatedStudents, RelatedExaminers
            this._onAllUserStoresLoaded();
        }
    },

    /**
     * Get the contents of the groups store (see {@link #getGroupsStore}
     * as an object with usernames as key and an array of
     * {@link subjectadmin.model.Group} records for values.
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
        this.getOverview().addClass('all-items-loaded'); // Mostly for the selenium tests, however someone may do something with it in a theme
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
        var tpl = Ext.create('Ext.XTemplate', dtranslate('subjectadmin.managestudents.multiselecthowto'));
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
        if(this.isProjectAssignment()) {
            translatekey = 'subjectadmin.groupunit.projectassignment';
        } else {
            translatekey = 'subjectadmin.groupunit.not_projectassignment';
        }
        if(pluralize) {
            translatekey += '_plural';
        }
        return dtranslate(translatekey);
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
