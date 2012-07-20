/**
 * List of groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.ListOfGroups' ,{
    extend: 'devilry_subjectadmin.view.managestudents.GridOfGroupsBase',
    alias: 'widget.listofgroups',
    cls: 'devilry_subjectadmin_listofgroups',
    store: 'Groups',
    hideHeaders: true,

    getColumns: function() {
        return [this.getGroupInfoColConfig(), this.getMetadataColConfig()];
    }
});
