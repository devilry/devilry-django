Ext.define('devilry.extjshelpers.studentsmanager.StudentsManager', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.studentsmanager',
    cls: 'studentsmanager',
    frame: false,
    border: false,

    requires: [
        'devilry.extjshelpers.studentsmanager.FilterSelector',
        'devilry.extjshelpers.studentsmanager.StudentsGrid',
        'devilry.extjshelpers.studentsmanager.ManuallyCreateUsers',
        'devilry.extjshelpers.assignmentgroup.MultiCreateNewDeadlineWindow',
        'devilry.extjshelpers.SearchField',
        'devilry.extjshelpers.SetListOfUsers',
        'devilry.gradeeditors.EditManyDraftEditorWindow'
    ],

    mixins: {
        manageExaminers: 'devilry.extjshelpers.studentsmanager.StudentsManagerManageExaminers',
        manageDeadlines: 'devilry.extjshelpers.studentsmanager.StudentsManagerManageDeadlines',
        createGroups: 'devilry.extjshelpers.studentsmanager.StudentsManagerManageGroups',
        createFeedback: 'devilry.extjshelpers.studentsmanager.StudentsManagerCreateFeedback',
        loadRelatedUsers: 'devilry.extjshelpers.studentsmanager.LoadRelatedUsersMixin',
        closeOpen: 'devilry.extjshelpers.studentsmanager.StudentsManagerCloseOpen'
    },

    config: {
        /**
         * @cfg
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false,

        deadlinemodel: undefined,
        assignmentgroupstore: undefined,
        assignmentid: undefined,
        gradeeditor_config_model: undefined,
        periodid: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);

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

        this.addStudentsButton = Ext.widget('button', {
            text: 'Create groups',
            iconCls: 'icon-add-32',
            scale: 'large',
            menu: [{
                text: Ext.String.format('One group for each student registered in {0}', DevilrySettings.DEVILRY_SYNCSYSTEM),
                listeners: {
                    scope: this,
                    click: this.onOneGroupForEachRelatedStudent
                }
            }, {
                text: 'Manually',
                listeners: {
                    scope: this,
                    click: this.onManuallyCreateUsers
                }
            }]
        });

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'searchfield',
                //width: 600,
                //height: 40,
                //padding: '30 0 0 0'
                //padding: 40,
                emptyText: 'Search...',
                margin: 10,
                flex: 0,

            //}, {
                //region:'west',
                //xtype: 'panel',
                //width: 200,
                //layout: 'fit',
                //items: [{
                    //xtype: 'studentsmanager_filterselector'
                //}]
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
                    items: [this.addStudentsButton, '->', {
                        xtype: 'button',
                        text: 'Actions on selected',
                        scale: 'large',
                        menu: [{
                            text: 'Close/open selected',
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
                            text: 'Add deadline to selected',
                            listeners: {
                                scope: this,
                                click: this.onAddDeadline
                            }
                        }, {
                            text: 'Change examiners on selected',
                            menu: [{
                                text: 'Replace',
                                iconCls: 'icon-edit-16',
                                listeners: {
                                    scope: this,
                                    click: this.onReplaceExaminers
                                }
                            }, {
                                text: 'Add',
                                iconCls: 'icon-add-16',
                                listeners: {
                                    scope: this,
                                    click: this.onAddExaminers
                                }
                            }, {
                                text: 'Random distribute',
                                listeners: {
                                    scope: this,
                                    click: this.onRandomDistributeExaminers
                                }
                            }, {
                                text: 'Clear',
                                iconCls: 'icon-delete-16',
                                listeners: {
                                    scope: this,
                                    click: this.onClearExaminers
                                }
                            }]
                        }]
                    }, this.giveFeedbackButton]
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
        this.assignmentgroupstore.load();
    },




    /**
     * @private
     */
    createRecordFromStoreRecord: function(record) {
        var editRecord = Ext.create('devilry.apps.administrator.simplified.SimplifiedAssignmentGroup', {
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
