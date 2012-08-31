Ext.define('devilry_subjectadmin.view.gradeeditor.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.gradeeditoroverview',
    cls: 'devilry_subjectadmin_gradeeditoroverview',

    requires: [
        'devilry_extjsextras.AlertMessageList'
    ],

    /**
     * @cfg {int} [assignment_id]
     * The ID of the assignment to load deadlines for.
     */

    frame: false,
    border: 0,
    bodyPadding: 40,
    autoScroll: true, // Autoscroll on overflow


    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'alertmessagelist',
                itemId: 'globalAlertmessagelist'
            }]
        });
        this.callParent(arguments);
    }
});
