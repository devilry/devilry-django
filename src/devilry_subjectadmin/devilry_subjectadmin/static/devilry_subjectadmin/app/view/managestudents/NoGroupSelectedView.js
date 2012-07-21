/**
 * A panel that displays information when no group is selected.
 */
Ext.define('devilry_subjectadmin.view.managestudents.NoGroupSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.nogroupselectedview',
    cls: 'nogroupselectedview bootstrap',
    ui: 'transparentpanel',
    padding: '20 20 10 0',

    /**
     * @cfg {string} topMessage (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'alertmessage',
                type: 'info',
                message: this.topMessage
            }]
        });
        this.callParent(arguments);
    }
});
