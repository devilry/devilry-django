/**
 * A panel that displays information about multple groups.
 */
Ext.define('subjectadmin.view.managestudents.MultipleGroupsSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.multiplegroupsview',
    cls: 'multiplegroupsview',
    ui: 'transparentpanel',

    /**
     * @cfg {[subjectadmin.model.Group]} groupRecords (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            html: Ext.String.format('Selected {0} groups', this.groupRecords.length)
        });
        this.callParent(arguments);
    }
});
