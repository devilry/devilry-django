/**
 * The grid that shows selected groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.SelectedGroupsSummaryGrid', {
    extend: 'devilry_subjectadmin.view.managestudents.GridOfGroupsBase',
    alias: 'widget.selectedgroupssummarygrid',
    cls: 'devilry_subjectadmin_selectedgroupssummarygrid',
    store: 'SelectedGroups',

    getColumns: function() {
        return [this.getGroupInfoColConfig(), this.getMetadataColConfig()];
    }
});
