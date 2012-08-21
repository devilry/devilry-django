/**
 * The grid that shows groups within a deadline.
 */
Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.GroupGrid', {
    extend: 'devilry_subjectadmin.view.managestudents.GridOfGroupsBase',
    alias: 'widget.bulkmanagedeadlines_groupgrid',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_groupgrid',
    store: 'SelectedGroups',
    disableSelection: true,
    hideHeaders: true,
    frame: false,

    getColumns: function() {
        return [
            this.getGroupInfoColConfig(),
            this.getMetadataColConfig()
        ];
    }
});
