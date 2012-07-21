/**
 * The grid that shows selected groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.SelectedGroupsSummaryGrid', {
    extend: 'devilry_subjectadmin.view.managestudents.GridOfGroupsBase',
    alias: 'widget.selectedgroupssummarygrid',
    cls: 'devilry_subjectadmin_selectedgroupssummarygrid',
    store: 'SelectedGroups',
    //disableSelection: true,

    title: gettext('Selected groups (click group to deselect it)'),

    getColumns: function() {
        return [
            this.getGroupInfoColConfig(),
            this.getMetadataColConfig(),
            this.getExaminersColConfig(),
            this.getTagsColConfig()
        ];
    },

    initComponent: function() {
        this.callParent(arguments);

        this.getView().on('render', function(view) {
            view.tip = Ext.create('Ext.tip.ToolTip', {
                target: view.el,
                delegate: view.itemSelector,
                showDelay: 50,
                trackMouse: true,
                renderTo: Ext.getBody(),
                listeners: {
                    // Change content dynamically depending on which element triggered the show.
                    beforeshow: function updateTipBody(tip) {
                        var groupRecord = view.getRecord(tip.triggerElement);
                        var group = groupRecord.getIdentString();
                        tip.update(Ext.String.format('Click to deselect "{0}"', group));
                    }
                }
            });
        });
    }
});
