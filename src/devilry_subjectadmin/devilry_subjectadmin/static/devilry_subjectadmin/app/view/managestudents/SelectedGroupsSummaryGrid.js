/**
 * The grid that shows selected groups on .
 */
Ext.define('devilry_subjectadmin.view.managestudents.SelectedGroupsSummaryGrid', {
    extend: 'devilry_subjectadmin.view.managestudents.ListOfGroups',
    alias: 'widget.selectedgroupssummarygrid',
    cls: 'devilry_subjectadmin_selectedgroupssummarygrid',
    hideHeaders: false,
    store: 'SelectedGroups',

    //initComponent: function() {
        //var me = this;
        //Ext.apply(this, {
        //});
        //this.callParent(arguments);
    //}
});
