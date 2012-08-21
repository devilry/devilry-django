Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.BulkManageDeadlinesPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.bulkmanagedeadlinespanel', // Define the widget xtype as allwhereisadminpanel
    cls: 'devilry_subjectadmin_bulkmanagedeadlinespanel',

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

    items: [{
        xtype: 'alertmessagelist',
        itemId: 'globalerrors'
    }]
});
