Ext.define('devilry.administrator.studentsmanager.StudentsManager', {
    extend: 'devilry.extjshelpers.studentsmanager.StudentsManager',
    alias: 'widget.administrator_studentsmanager',

    mixins: {
        manageExaminers: 'devilry.administrator.studentsmanager.StudentsManagerManageExaminers',
        createGroups: 'devilry.administrator.studentsmanager.StudentsManagerManageGroups',
        loadRelatedUsers: 'devilry.administrator.studentsmanager.LoadRelatedUsersMixin'
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    getToolbarItems: function() {
        var defaults = this.callParent();
        defaults[0] = this.addStudentsButton;
        Ext.Array.insert(defaults, 1, '->');
        return defaults;
    },

    getOnSelectedMenuItems: function() {
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
        return menu;
    }
});
