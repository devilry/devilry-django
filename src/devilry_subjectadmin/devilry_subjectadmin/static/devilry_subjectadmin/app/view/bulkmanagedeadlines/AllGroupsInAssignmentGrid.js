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
            //features: [this.groupingFeature],
            //groupHeaderTpl: '',
            selModel: Ext.create('Ext.selection.CheckboxModel')
        });
        this.callParent(arguments);
    }
});
