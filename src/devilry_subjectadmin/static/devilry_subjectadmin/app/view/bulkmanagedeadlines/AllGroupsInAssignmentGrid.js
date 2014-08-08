/*
 * The grid that allows users to select specific groups when adding a deadline.
 */
Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.AllGroupsInAssignmentGrid', {
    extend: 'devilry_subjectadmin.view.managestudents.GridOfGroupsBase',
    alias: 'widget.bulkmanagedeadlines_allgroupsgrid',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_allgroupsgrid',
    store: 'Groups',
    hideHeaders: true,
    frame: false,

    requires: [
        'devilry_subjectadmin.view.managestudents.SelectedGroupsButton',
        'devilry_extjsextras.GridBigButtonCheckboxModel',
        'devilry_subjectadmin.view.managestudents.SelectGroupsBySearchWidget'
    ],

    /**
     * @cfg {int} [assignment_id]
     * The ID of the assignment we are listing students in.
     */

    getColumns: function() {
        return [
            this.getGroupInfoColConfig(),
            this.getMetadataColConfig()
        ];
    },

    initComponent: function() {
        Ext.apply(this, {
            selModel: Ext.create('devilry_extjsextras.GridBigButtonCheckboxModel'),

            tbar: [{
                text: gettext('Select'),
                menu: [{
                    text: gettext('Select all'),
                    listeners: {
                        scope: this,
                        click: this._onSelectAll
                    }
                }, {
                    text: gettext('Deselect all'),
                    listeners: {
                        scope: this,
                        click: this._onDeSelectAll
                    }
                }]
            }, {
                xtype: 'selectgroupsbysearch',
                grid: this,
                flex: 1
            }, {
                xtype: 'selectedgroupsbutton',
                grid: this
            }]
        });
        this.callParent(arguments);
    },

    _onSelectAll: function() {
        this.getSelectionModel().selectAll();
    },
    _onDeSelectAll: function() {
        this.getSelectionModel().deselectAll();
    }
});
