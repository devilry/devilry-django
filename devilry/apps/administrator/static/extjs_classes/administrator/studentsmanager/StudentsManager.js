Ext.define('devilry.administrator.studentsmanager.StudentsManager', {
    extend: 'devilry.extjshelpers.studentsmanager.StudentsManager',
    alias: 'widget.administrator_studentsmanager',

    mixins: {
        manageExaminers: 'devilry.administrator.studentsmanager.StudentsManagerManageExaminers',
        createGroups: 'devilry.administrator.studentsmanager.StudentsManagerManageGroups',
        loadRelatedUsers: 'devilry.administrator.studentsmanager.LoadRelatedUsersMixin',
        loadRelatedUsers: 'devilry.administrator.studentsmanager.AddDeliveriesMixin'
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
        defaults[0] = this.addStudentsButton;
        Ext.Array.insert(defaults, 1, '->');
        return defaults;
    },

    getOnSingleMenuItems: function() {
        var menu = this.callParent();
        menu.push({
            text: 'Edit group details',
            iconCls: 'icon-edit-16',
            listeners: {
                scope: this,
                click: function() { Ext.MessageBox.alert('Not available yet', 'Coming soon') }
            }
        });
        //menu.push({
            //text: 'Mark as approved in a previous period',
            //listeners: {
                //scope: this,
                //click: this.onPreviouslyApproved
            //}
        //});
        menu.push({
            text: 'Create dummy delivery',
            listeners: {
                scope: this,
                click: this.onCreateDummyDelivery
            }
        });
        return menu;
    },

    getOnManyMenuItems: function() {
        var menu = this.callParent();
        menu.push({
            text: 'Change examiners',
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
        });
        menu.push({
            text: 'Delete',
            iconCls: 'icon-delete-16',
            listeners: {
                scope: this,
                click: function() { Ext.MessageBox.alert('Not available yet', 'Coming soon') }
            }
        });
        return menu;
    }
});
