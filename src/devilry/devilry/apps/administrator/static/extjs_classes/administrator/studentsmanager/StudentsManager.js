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
            text: interpolate(gettext('Add %(students_term)s'), {
                students_term: gettext('students')
            }, true),
            iconCls: 'icon-add-32',
            scale: 'large',
            menu: [{
                text: interpolate(gettext('Import %(students_term)s registered in %(syncsystem)s'), {
                    students_term: gettext('students'),
                    syncsystem: DevilrySettings.DEVILRY_SYNCSYSTEM
                }, true),
                listeners: {
                    scope: this,
                    click: this.onOneGroupForEachRelatedStudent
                }
            }, {
                text: interpolate(gettext('Import from another %(assignment_term)s'), {
                    assignment_term: gettext('assignment')
                }, true),
                listeners: {
                    scope: this,
                    click: this.onImportGroupsFromAnotherAssignmentInCurrentPeriod
                }
            }, {
                text: gettext('Manually'),
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
            text: interpolate(gettext('Set %(examiners_term)s'), {
                examiners_term: gettext('examiners')
            }, true),
            scale: 'large',
            menu: this.getSetExaminersMenuItems()
        }]);
        return defaults;
    },

    getSetExaminersMenuItems: function() {
        return [{
            text: gettext('Replace'),
            iconCls: 'icon-edit-16',
            listeners: {
                scope: this,
                click: this.onReplaceExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: interpolate(gettext('Replace %(examiners_term)s'), {
                            examiners_term: gettext('examiners')
                        }, true),
                        html: interpolate(gettext('Replace %(examiners_term)s on the selected %(groups_term)s (removes current %(examiners_term)s).'), {
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups')
                        }, true)
                    });
                }
            }
        }, {
            text: gettext('Add'),
            iconCls: 'icon-add-16',
            listeners: {
                scope: this,
                click: this.onAddExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: interpolate(gettext('Add %(examiners_term)s'), {
                            examiners_term: gettext('examiners')
                        }, true),
                        html: interpolate(gettext('Add %(examiners_term)s to the selected %(groups_term)s.'), {
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups')
                        }, true)
                    });
                }
            }
        }, {
            text: gettext('Random distribute'),
            listeners: {
                scope: this,
                click: this.onRandomDistributeExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        html: interpolate(gettext('Random distribute a list of %(examiners_term)s to the selected %(groups_term)s. Replaces current %(examiners_term)s on the selected %(groups_term)s.'), {
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups')
                        }, true)
                    });
                }
            }
        }, {
            text: interpolate(gettext('Copy from another %(assignment_term)s'), {
                assignment_term: gettext('assignment')
            }, true),
            listeners: {
                scope: this,
                click: this.onImportExaminersFromAnotherAssignmentInCurrentPeriod,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: interpolate(gettext('Copy from another %(assignment_term)s'), {
                            assignment_term: gettext('assignment')
                        }, true),
                        html: interpolate(gettext('Lets you choose another %(assignment_term)s, and import %(examiners_term)s. Replaces current %(examiners_term)s on the selected %(groups_term)s.'), {
                            assignment_term: gettext('assignment'),
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups')
                        }, true)
                    });
                }
            }
        }, {
            text: gettext('Automatically'),
            listeners: {
                scope: this,
                click: this.onSetExaminersFromTags,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: interpolate(gettext('Automatically set %(examiners_term)'), {
                            examiners_term: gettext('examiners')
                        }, true),
                        html: interpolate(gettext('Match tagged %(examiners_term)s to equally tagged %(groups_term)s. Tags are normally imported from %(syncsystem)s.'), {
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups'),
                            syncsystem: DevilrySettings.DEVILRY_SYNCSYSTEM
                        }, true)
                    });
                }
            }
        }, {
            text: gettext('Clear'),
            iconCls: 'icon-delete-16',
            listeners: {
                scope: this,
                click: this.onClearExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: gettext('Clear'),
                        html: interpolate(gettext('Remove all %(examiners_term)s on selected %(groups_term)s.'), {
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups')
                        }, true)
                    });
                }
            }
        }];
    },

    getContexMenuManySelectItems: function() {
        var defaultItems = this.callParent();
        return Ext.Array.merge(defaultItems, [{
            text: interpolate(gettext('Set %(examiners_term)s'), {
                examiners_term: gettext('examiners')
            }, true),
            menu: this.getSetExaminersMenuItems()
        }]);
    },

    getFilters: function() {
        var defaultFilters = this.callParent();
        var me = this;
        var adminFilters = [{xtype: 'menuheader', html: 'Missing users'}, {
            text: interpolate(gettext('Has no %(students_term)s'), {
                students_term: gettext('students')
            }, true),
            handler: function() { me.setFilter('candidates__student__username:none'); }
        }, {
            text: interpolate(gettext('Has no %(examiners_term)s'), {
                examiners_term: gettext('examiners')
            }, true),
            handler: function() { me.setFilter('examiners__user__username:none'); }
        }];
        Ext.Array.insert(adminFilters, 0, defaultFilters);
        return adminFilters;
    },

    getOnSingleMenuItems: function() {
        var menu = this.callParent();
        menu.push({
            text: gettext('Change group members'),
            iconCls: 'icon-edit-16',
            listeners: {
                scope: this,
                click: this.onChangeGroupMembers
            }
        });
        menu.push({
            text: gettext('Change group name'),
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
            text: interpolate(gettext('Mark as delivered in a previous %(period_term)s'), {
                period_term: gettext('period')
            }, true),
            listeners: {
                scope: this,
                click: this.onPreviouslyPassed
            }
        });
        menu.push({
            text: gettext('Delete'),
            iconCls: 'icon-delete-16',
            listeners: {
                scope: this,
                click: this.onDeleteGroups
            }
        });
        if(this.assignmentrecord.data.anonymous) {
            menu.push({
                text: gettext('Import candidate IDs'),
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
            var model = Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedAssignmentGroup');
            var assignmentGroupStore = Ext.create('Ext.data.Store', {
                model: model,
                remoteFilter: true,
                remoteSort: true
            });

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
