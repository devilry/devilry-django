/**
 * A panel that displays information about a single group.
 */
Ext.define('subjectadmin.view.managestudents.SingleGroupSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.singlegroupview',
    cls: 'singlegroupview',
    ui: 'transparentpanel',

    /**
     * @cfg {string} topMessage (required)
     */

    /**
     * @cfg {string} multiselectHowto (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'alertmessage',
                type: 'info',
                message: [this.topMessage, this.multiselectHowto].join(' ')
            }]
        });
        this.callParent(arguments);
    }
});
