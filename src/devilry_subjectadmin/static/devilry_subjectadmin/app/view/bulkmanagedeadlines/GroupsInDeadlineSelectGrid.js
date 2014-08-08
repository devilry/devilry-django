/**
 * The grid used to select groups when only applying deadline changes to some groups.
 */
Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.GroupsInDeadlineSelectGrid', {
    extend: 'devilry_subjectadmin.view.bulkmanagedeadlines.GroupsInDeadlineGrid',
    alias: 'widget.bulkmanagedeadlines_groupsindeadlineselectgrid',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_groupsindeadlineselectgrid',
    disableSelection: false,
    hideHeaders: true,
    frame: false,

    requires: [
        'devilry_subjectadmin.view.managestudents.SelectedGroupsButton',
        'devilry_extjsextras.GridBigButtonCheckboxModel',
        'devilry_subjectadmin.view.managestudents.SelectGroupsBySearchWidget'
    ],

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

    getGroupUrlPrefix: function() {
        return null;
    },

    _onSelectAll: function() {
        this.getSelectionModel().selectAll();
    },
    _onDeSelectAll: function() {
        this.getSelectionModel().deselectAll();
    }
});
