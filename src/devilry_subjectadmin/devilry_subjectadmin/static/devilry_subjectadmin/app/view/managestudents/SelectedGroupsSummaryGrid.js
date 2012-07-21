/**
 * The grid that shows selected groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.SelectedGroupsSummaryGrid', {
    extend: 'devilry_subjectadmin.view.managestudents.GridOfGroupsBase',
    alias: 'widget.selectedgroupssummarygrid',
    cls: 'devilry_subjectadmin_selectedgroupssummarygrid',
    store: 'SelectedGroups',
    disableSelection: true,

    requires: [
        'devilry_subjectadmin.view.managestudents.AutocompleteGroupWidget'
    ],

    getColumns: function() {
        return [
            this.getGroupInfoColConfig(),
            this.getMetadataColConfig(),
            this.getExaminersColConfig(),
        ];
    },

    initComponent: function() {
        Ext.apply(this, {
            fbar: [{
                xtype: 'autocompletegroupwidget',
                flex: 1,
                hideTrigger: true,
                itemId: 'selectUsersByAutocompleteWidget'
            }]
        });
        this.callParent(arguments);
    }
});
