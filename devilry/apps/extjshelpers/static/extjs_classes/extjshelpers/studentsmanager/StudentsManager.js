Ext.define('devilry.extjshelpers.studentsmanager.StudentsManager', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.studentsmanager',
    cls: 'studentsmanager',
    frame: false,
    border: false,

    requires: [
        'devilry.extjshelpers.studentsmanager.FilterSelector',
        'devilry.extjshelpers.studentsmanager.StudentsGrid',
        'devilry.extjshelpers.assignmentgroup.MultiCreateNewDeadlineWindow',
        'devilry.extjshelpers.SearchField',
        'devilry.extjshelpers.SetListOfUsers',
        'devilry.gradeeditors.EditManyDraftEditorWindow'
    ],

    mixins: {
        createFeedback: 'devilry.extjshelpers.studentsmanager.StudentsManagerCreateFeedback',
        manageDeadlines: 'devilry.extjshelpers.studentsmanager.StudentsManagerManageDeadlines',
        closeOpen: 'devilry.extjshelpers.studentsmanager.StudentsManagerCloseOpen'
    },

    config: {
        /**
         * @cfg
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false,
        gradeeditor_config_model: undefined,
        deadlinemodel: undefined,
        assignmentid: undefined,
        assignmentgroupstore: undefined,

        periodid: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);

        this.role = this.isAdministrator? 'administrator': 'examiner';
        this.gradeeditor_config_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.registryitem_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.registryitem_recordcontainer.addListener('setRecord', this.onLoadRegistryItem, this);
    },

    initComponent: function() {
        this.giveFeedbackButton = Ext.widget('button', {
            scale: 'large',
            text: 'Give feedback to selected',
            listeners: {
                scope: this,
                click: this.onGiveFeedbackToSelected,
                render: function(button) {
                    if(!this.registryitem_recordcontainer.record) {
                        button.getEl().mask('Loading'); // TODO: Only mask the affected buttons
                    }
                }
            }
        });

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'searchfield',
                emptyText: 'Search...',
                margin: 10,
                flex: 0,
            }, {
                xtype: 'panel',
                flex: 1,
                layout: 'fit',
                frame: true,
                border: false,
                items: [{
                    xtype: 'studentsmanager_studentsgrid',
                    store: this.assignmentgroupstore,
                    assignmentid: this.assignmentid
                }],

                dockedItems: [{
                    xtype: 'toolbar',
                    dock: 'bottom',
                    ui: 'footer',
                    items: this.getToolbarItems()
                }]
            }],

        });
        this.callParent(arguments);
        this.setSearchfieldAttributes();

        this.addListener('render', function() {
            //this.up('window').addListener('show', this.onManuallyCreateUsers, this);
            //this.up('window').addListener('show', this.onOneGroupForEachRelatedStudent, this);
        }, this);
        this.loadGradeEditorConfigModel();

        this.loadFirstPage();
    },

    getToolbarItems: function() {
        return ['->', {
            xtype: 'button',
            text: 'Actions on selected',
            scale: 'large',
            menu: this.getOnSelectedMenuItems()
        }, this.giveFeedbackButton];
    },

    getOnSelectedMenuItems: function() {
        return [{
            text: 'Close/open',
            menu: [{
                text: 'Close',
                listeners: {
                    scope: this,
                    click: this.onCloseGroups
                }
            }, {
                text: 'Open',
                listeners: {
                    scope: this,
                    click: this.onOpenGroups
                }
            }]
        }, {
            text: 'Add deadline',
            listeners: {
                scope: this,
                click: this.onAddDeadline
            }
        }];
    },

    /**
     * @private
     */
    onSelectNone: function() {
        Ext.MessageBox.alert('No element(s) selected', 'You must select at least one group to use the selected action.');
    },

    /**
     * @private
     */
    noneSelected: function() {
        return this.down('studentsmanager_studentsgrid').selModel.getSelection().length == 0;
    },

    /**
     * @private
     */
    loadFirstPage: function() {
        this.assignmentgroupstore.currentPage = 1;
        this.refreshStore();
    },




    /**
     * @private
     */
    createRecordFromStoreRecord: function(record) {
        var modelname = Ext.String.format('devilry.apps.{0}.simplified.SimplifiedAssignmentGroup', this.role);
        var editRecord = Ext.create(modelname, {
            // NOTE: Very important that this is all the editablefields, since any missing fields will be None!
            id: record.data.id,
            name: record.data.name,
            is_open: record.data.is_open,
            parentnode: record.data.parentnode,
        });
        return editRecord;
    },

    
    /**
     * @private
     */
    setSearchfieldAttributes: function() {
        var searchfield = this.down('searchfield');
        searchfield.addListener('newSearchValue', this.search, this);
        searchfield.addListener('emptyInput', function() {
            this.search("");
        }, this);
    },
    
    /**
     * @private
     */
    search: function(searchstring) {
        var parsedSearch = Ext.create('devilry.extjshelpers.SearchStringParser', {
            searchstring: searchstring
        });
        var extraParams = this.assignmentgroupstore.proxy.extraParams;
        this.assignmentgroupstore.proxy.extraParams = parsedSearch.applyToExtraParams(extraParams, []);
        this.assignmentgroupstore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode',
            comp: 'exact',
            value: this.assignmentid
        }]);
        this.assignmentgroupstore.loadPage(1, {
            scope: this,
            callback: function(records, operation, success) {
            }
        });
    },

    /**
     * @private
     * Reftesh store by re-searching for the current value.
     */
    refreshStore: function() {
        var searchfield = this.down('searchfield');
        this.search(searchfield.getValue());
    }
});
