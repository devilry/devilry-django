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

    getGroupUrlPrefix: function() {
        return devilry_subjectadmin.utils.UrlLookup.manageSpecificGroupsPrefix(this.assignment_id);
    }
});
