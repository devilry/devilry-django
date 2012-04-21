/**
 * A panel that displays information about multple groups.
 */
Ext.define('subjectadmin.view.managestudents.MultipleGroupsSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.multiplegroupsview',
    cls: 'multiplegroupsview',
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
            }, {
                xtype: 'box',
                cls: 'bootstrap',
                html: '<strong>NOTE:</strong> This view is incomplete. Please see <a href="http://heim.ifi.uio.no/espeak/devilry-figures/managestudents-multiselect.png" target="_blank">this image mockup</a> of the planned interface.'
            }]
        });
        this.callParent(arguments);
    }
});
