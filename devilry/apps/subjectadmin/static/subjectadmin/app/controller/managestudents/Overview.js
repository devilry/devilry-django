/**
 * Controller for the managestudents overview.
 */
Ext.define('subjectadmin.controller.managestudents.Overview', {
    extend: 'Ext.app.Controller',

    mixins: {
        'loadAssignment': 'subjectadmin.utils.LoadAssignmentMixin'
    },

    views: [
        'managestudents.Overview',
        'managestudents.ListOfGroups'
    ],

    /**
     * Get the related examiners store.
     * @return {subjectadmin.store.RelatedExaminers} Store.
     * @method getRelatedExaminersStore
     */

    /**
     * Get the related students store.
     * @return {subjectadmin.store.RelatedStudents} Store.
     * @method getRelatedStudentsStore
     */

    /**
     * Get the groups store.
     * @return {subjectadmin.store.Groups} Store.
     * @method getGroupsStore
     */

    stores: [
        'SingleAssignment',
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
     * @method getListofgroupsToolbar
     */

    refs: [{
        ref: 'overview',
        selector: 'managestudentsoverview'
    }, {
        ref: 'listofgroupsToolbar',
        selector: 'toolbar[itemId=listofgroupsToolbar]'
    }],

    init: function() {
        this.control({
            'viewport managestudentsoverview': {
                render: this._onRender
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

    getSubjectShortname: function() {
        return this.subject_shortname;
    },
    getPeriodShortname: function() {
        return this.period_shortname;
    },
    getAssignmentShortname: function() {
        return this.assignment_shortname;
    },

    getMaskElement: function() {
        return this.getOverview().getEl();
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

    _onAllUserStoresLoaded: function() {
        this.getOverview().setLoading(false);
        this.getOverview().addClass('all-items-loaded'); // Mostly for the selenium tests, however someone may do something with it in a theme
        this.application.fireEvent('managestudentsSuccessfullyLoaded', this);
    }
});
