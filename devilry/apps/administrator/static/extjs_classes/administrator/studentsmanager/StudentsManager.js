Ext.define('devilry.administrator.studentsmanager.StudentsManager', {
    extend: 'devilry.extjshelpers.studentsmanager.StudentsManager',
    alias: 'widget.administrator_studentsmanager',
    requires: [
        'devilry.extjshelpers.studentsmanager.ImportGroupsFromAnotherAssignment'
    ],

    mixins: {
        manageExaminers: 'devilry.administrator.studentsmanager.StudentsManagerManageExaminers',
        createGroups: 'devilry.administrator.studentsmanager.StudentsManagerManageGroups',
        loadRelatedUsers: 'devilry.administrator.studentsmanager.LoadRelatedUsersMixin',
        addDeliveries: 'devilry.administrator.studentsmanager.AddDeliveriesMixin'
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
                text: 'From another assignment',
                listeners: {
                    scope: this,
                    click: this.onImportExaminersFromAnotherAssignmentInCurrentPeriod
                }
            }, {
                text: 'Clear',
                iconCls: 'icon-delete-16',
                listeners: {
                    scope: this,
                    click: this.onClearExaminers
                }
            }]
        }]);
        return defaults;
    },

    getFilters: function() {
        var defaultFilters = this.callParent();
        var me = this;
        var adminFilters = ['-', {
            text: 'Has no students',
            handler: function() { me.setFilter('candidates__student__username:none'); }
        }, {
            text: 'Has no examiners',
            handler: function() { me.setFilter('examiners__username:none'); }
        }];
        Ext.Array.insert(adminFilters, 0, defaultFilters);
        return adminFilters;
    },

    getOnSingleMenuItems: function() {
        var menu = this.callParent();
        //menu.push({
            //text: 'Create dummy delivery',
            //listeners: {
                //scope: this,
                //click: this.onCreateDummyDelivery
            //}
        //});
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
        return menu;
    }
});
