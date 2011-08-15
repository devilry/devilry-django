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
        'devilry.extjshelpers.SearchField',
        'devilry.extjshelpers.SetListOfUsers',
        'devilry.gradeeditors.EditManyDraftEditorWindow'
    ],

    config: {
        /**
         * @cfg
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false,

        assignmentgroupstore: undefined,
        assignmentid: undefined,
        gradeeditor_config_model: undefined
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
            text: 'Add students',
            iconCls: 'icon-add-32',
            scale: 'large',
            listeners: {
                scope: this,
                click: this.onManuallyCreateUsers
            }
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
                        text: 'Change examiners on selected',
                        scale: 'large',
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
                                scope: this
                            }
                        }, {
                            text: 'Clear',
                            iconCls: 'icon-delete-16',
                            listeners: {
                                scope: this,
                                click: this.onClearExaminers
                            }
                        }]
                    }, this.giveFeedbackButton]
                }]
            }],

        });
        this.callParent(arguments);
        this.setSearchfieldAttributes();

        //this.addListener('render', function() {
            //this.up('window').addListener('show', this.onManuallyCreateUsers, this);
        //}, this);
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
    onSetExaminers: function(append) {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var win = Ext.widget('window', {
            title: 'Set examiners',
            modal: true,
            width: 500,
            height: 400,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                //usernames: ['donald', 'scrooge'],
                usernames: [],
                helptext: '<p>The username of a single examiner on each line. Example:</p>',
                listeners: {
                    scope: this,
                    saveClicked: function(setlistofusersobj, usernames) {
                        this.setExaminersOnSelected(setlistofusersobj, usernames, append);
                    }
                }
            },
        });
        win.show();
    },


    /**
     * @private
     */
    onAddExaminers: function() {
        this.onSetExaminers(true);
    },

    /**
     * @private
     */
    onReplaceExaminers: function() {
        this.onSetExaminers(false);
    },

    /**
     * @private
     */
    onClearExaminers: function() {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }

        Ext.MessageBox.show({
            title: 'Confirm clear examiners?',
            msg: 'Are you sure you want to clear examiners on all the selected items?',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.WARNING,
            scope: this,
            fn: function(btn) {
                if(btn == 'yes') {
                    this.down('studentsmanager_studentsgrid').performActionOnSelected({
                        scope: this,
                        callback: this.setExaminers,
                        extraArgs: [[], false]
                    });
                }
            }
        });

    },


    /**
     * @private
     */
    setExaminersOnSelected: function(setlistofusersobj, usernames, append) {
        setlistofusersobj.up('window').close();
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.setExaminers,
            extraArgs: [usernames, append]
        });
    },

    /**
     * @private
     */
    setExaminers: function(record, index, total, usernames, append) {
        var msg = Ext.String.format('Setting examiners on group {0}/{1}', index, total);
        this.getEl().mask(msg);

        if(append) {
            //console.log(record);
            usernames = Ext.Array.merge(usernames, record.data.examiners__username);
            //console.log(usernames);
        };

        var editRecord = Ext.create('devilry.apps.administrator.simplified.SimplifiedAssignmentGroup', {
            // NOTE: Very important that this is all the editablefields, since any missing fields will be None!
            id: record.data.id,
            name: record.data.name,
            is_open: record.data.is_open,
            parentnode: record.data.parentnode,
            fake_examiners: usernames
        });

        editRecord.save({
            failure: function() {
                console.error('Failed to save record');
            }
        });

        if(index == total) {
            this.loadFirstPage();
            this.getEl().unmask();
        }
    },

    /**
     * @private
     */
    loadGradeEditorConfigModel: function() {
        this.gradeeditor_config_model.load(this.assignmentid, {
            scope: this,
            success: function(record) {
                this.gradeeditor_config_recordcontainer.setRecord(record);
                this.loadRegistryItem();
            },
            failure: function() {
                // TODO: Handle errors
            }
        });
    },

    /**
     * @private
     */
    loadRegistryItem: function() {
        var registryitem_model = Ext.ModelManager.getModel('devilry.gradeeditors.RestfulRegistryItem');
        registryitem_model.load(this.gradeeditor_config_recordcontainer.record.data.gradeeditorid, {
            scope: this,
            success: function(record) {
                this.registryitem_recordcontainer.setRecord(record);
            }
        });
    },

    /**
     * @private
     */
    onLoadRegistryItem: function() {
        if(this.giveFeedbackButton.rendered) {
            this.giveFeedbackButton.getEl().unmask();
        }
    },

    /**
     * @private
     */
    onGiveFeedbackToSelected: function(button) {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var draftEditor = Ext.create('devilry.gradeeditors.EditManyDraftEditorWindow', {
            isAdministrator: this.isAdministrator,
            gradeeditor_config: this.gradeeditor_config_recordcontainer.record.data,
            registryitem: this.registryitem_recordcontainer.record.data,
            listeners: {
                scope: this,
                createNewDraft: this.onPublishFeedback
            }
        });
        draftEditor.show();
    },


    /**
     * @private
     */
    onPublishFeedback: function(feedbackdraftModelName, draftstring) {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.giveFeedbackToSelected,
            extraArgs: [feedbackdraftModelName, draftstring]
        });
    },

    /**
     * @private
     */
    giveFeedbackToSelected: function(record, index, total, feedbackdraftModelName, draftstring) {
        //console.log(feedbackdraftModelName);
        var msg = Ext.String.format('Setting feedback on group {0}/{1}', index, total);
        this.getEl().mask(msg);

        if(record.data.latest_delivery_id != null) {
            var draftrecord = Ext.create(feedbackdraftModelName, {
                draft: draftstring,
                published: true,
                delivery: record.data.latest_delivery_id
            });
            draftrecord.save({
                scope: this,
                failure: function() {
                    console.error('Failed to save a draft');
                    console.error(draftrecord);
                }
            });
        }

        if(index == total) {
            this.loadFirstPage();
            this.getEl().unmask();
        }
    },
    
    /**
     * @private
     */
    onManuallyCreateUsers: function() {
        var win = Ext.widget('window', {
            title: 'Create assignment groups',
            modal: true,
            width: 830,
            height: 600,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'manuallycreateusers',
                assignmentid: this.assignmentid
            },
            listeners: {
                scope: this,
                close: function() {
                    this.refreshStore();
                }
            }
        });
        win.show();
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
                //console.log(records);
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
