Ext.define('devilry.administrator.studentsmanager.StudentsManager', {
    extend: 'devilry.extjshelpers.studentsmanager.StudentsManager',
    alias: 'widget.administrator_studentsmanager',
    requires: [
        'devilry.extjshelpers.studentsmanager.ImportGroupsFromAnotherAssignment'
    ],

    mixins: {
        manageExaminers: 'devilry.administrator.studentsmanager.StudentsManagerManageExaminers',
        createGroups: 'devilry.administrator.studentsmanager.StudentsManagerManageGroups',
        loadRelatedUsers: 'devilry.administrator.studentsmanager.LoadRelatedUsersMixin'
    },

    //config: {
        //assignmentgroupPrevApprovedStore: undefined
    //},

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.addStudentsButton = Ext.widget('button', {
            text: 'Add students',
            iconCls: 'icon-add-32',
            scale: 'large',
            menu: [{
                text: Ext.String.format('Import students registered in {0}', DevilrySettings.DEVILRY_SYNCSYSTEM),
                listeners: {
                    scope: this,
                    click: this.onOneGroupForEachRelatedStudent
                }
            }, {
                text: 'Import from another assignment',
                listeners: {
                    scope: this,
                    click: this.onImportGroupsFromAnotherAssignmentInCurrentPeriod
                }
            }, {
                text: 'Manually',
                listeners: {
                    scope: this,
                    click: this.onManuallyCreateUsers
                }
            }]
        });

        this.callParent(arguments);
    },

    getToolbarItems: function() {
        var defaults = this.callParent();
        Ext.Array.insert(defaults, 2, [this.addStudentsButton, {
            xtype: 'button',
            text: 'Set examiners',
            scale: 'large',
            menu: this.getSetExaminersMenuItems()
        }]);
        return defaults;
    },

    getSetExaminersMenuItems: function() {
        return [{
            text: 'Replace',
            iconCls: 'icon-edit-16',
            listeners: {
                scope: this,
                click: this.onReplaceExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: 'Replace examiners',
                        html: 'Replace examiners to the selected groups (removes current examiners).'
                    });
                }
            }
        }, {
            text: 'Add',
            iconCls: 'icon-add-16',
            listeners: {
                scope: this,
                click: this.onAddExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: 'Add examiners',
                        html: 'Add examiners to the selected groups.'
                    });
                }
            }
        }, {
            text: 'Random distribute',
            listeners: {
                scope: this,
                click: this.onRandomDistributeExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: 'Random distribute',
                        html: 'Random distribute a list of examiners to the selected groups. Replaces current examiners on the selected groups.'
                    });
                }
            }
        }, {
            text: 'Copy from another assignment',
            listeners: {
                scope: this,
                click: this.onImportExaminersFromAnotherAssignmentInCurrentPeriod,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: 'Copy from another assignment',
                        html: 'Lets you choose another assignment, and import examiners. Replaces current examiners on the selected groups.'
                    });
                }
            }
        }, {
            text: 'Automatically',
            listeners: {
                scope: this,
                click: this.onSetExaminersFromTags,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: 'Automatically set examiners',
                        html: Ext.String.format('Match tagged examiners to equally tagged groups. Tags are normally imported from {0}.', DevilrySettings.DEVILRY_SYNCSYSTEM)
                    });
                }
            }
        }, {
            text: 'Clear',
            iconCls: 'icon-delete-16',
            listeners: {
                scope: this,
                click: this.onClearExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: 'Clear',
                        html: 'Remove all examiners on selected groups.'
                    });
                }
            }
        }];
    },

    getContexMenuManySelectItems: function() {
        var defaultItems = this.callParent();
        return Ext.Array.merge(defaultItems, [{
            text: 'Set examiners',
            menu: this.getSetExaminersMenuItems()
        }]);
    },

    getFilters: function() {
        var defaultFilters = this.callParent();
        var me = this;
        var adminFilters = [{xtype: 'menuheader', html: 'Missing users'}, {
            text: 'Has no students',
            handler: function() { me.setFilter('candidates__student__username:none'); }
        }, {
            text: 'Has no examiners',
            handler: function() { me.setFilter('examiners__user__username:none'); }
        }];
        Ext.Array.insert(adminFilters, 0, defaultFilters);
        return adminFilters;
    },

    getOnSingleMenuItems: function() {
        var menu = this.callParent();
        menu.push({
            text: 'Change group members',
            iconCls: 'icon-edit-16',
            listeners: {
                scope: this,
                click: this.onChangeGroupMembers
            }
        });
        menu.push({
            text: 'Change group name',
            iconCls: 'icon-edit-16',
            listeners: {
                scope: this,
                click: this.onChangeGroupName
            }
        });
        return menu;
    },

    getOnManyMenuItems: function() {
        var menu = this.callParent();
        menu.push({
            text: 'Mark as delivered in a previous period',
            listeners: {
                scope: this,
                click: this.onPreviouslyPassed
            }
        });
        menu.push({
            text: 'Delete',
            iconCls: 'icon-delete-16',
            listeners: {
                scope: this,
                click: this.onDeleteGroups
            }
        });
        if(this.assignmentrecord.data.anonymous) {
            menu.push({
                text: 'Import candidate IDs',
                listeners: {
                    scope: this,
                    click: this.onSetCandidateIdBulk
                }
            });
        }
        return menu;
    },

    _addMenuItemTooltip: function(menuitem, args) {
        Ext.create('Ext.tip.ToolTip', Ext.apply(args, {
            target: menuitem.getEl(),
            showDelay: 50,
            width: 300,
            anchor: 'left',
            dismissDelay: 30000 // Hide after 30 seconds hover
        }));
    },

    statics: {
        getAllGroupsInAssignment: function(assignmentid, action) {
            assignmentGroupModel = Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedAssignmentGroupImport');
            var assignmentGroupStore = Ext.create('Ext.data.Store', {
                model: assignmentGroupModel,
                proxy: Ext.create('devilry.extjshelpers.RestProxy', {
                    url: assignmentGroupModel.proxy.url
                })
            });
            assignmentGroupStore.proxy.setDevilryResultFieldgroups(['users', 'tags']);

            assignmentGroupStore.proxy.setDevilryFilters([{
                field: 'parentnode',
                comp: 'exact',
                value: assignmentid
            }]);

            assignmentGroupStore.pageSize = 1;
            assignmentGroupStore.load({
                scope: this,
                callback: function(records, op, success) {
                    if(!success) {
                        this.loadAssignmentGroupStoreFailed();
                    }
                    assignmentGroupStore.pageSize = assignmentGroupStore.totalCount;
                    assignmentGroupStore.load({
                        scope: this,
                        callback: function(records, op, success) {
                            Ext.bind(action.callback, action.scope, action.extraArgs, true)(records, op, success);
                        }
                    });
                }
            });
        }
    }
});
