/**
 * Related students overview.
 */
Ext.define('devilry_subjectadmin.view.relatedstudents.Overview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.relatedstudents',
    cls: 'devilry_subjectadmin_relatedstudents',
    requires: [
        'Ext.layout.container.Column',
        'devilry_extjsextras.AlertMessageList'
    ],

    frame: false,
    border: 0,
    bodyPadding: 40,
    autoScroll: true,


    /**
     * @cfg {String} period_id (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'alertmessagelist'
            }, {
                xtype: 'box',
                html: 'hei'
            }]
        });
        this.callParent(arguments);
    }
});
