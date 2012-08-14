Ext.define('devilry_student.view.groupinfo.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.groupinfo',
    cls: 'devilry_student_groupinfo',

    frame: false,
    border: 0,
    bodyPadding: 20,
    autoScroll: true,

    items: [{
        xtype: 'box',
        itemId: 'metadata'
    }, {
        xtype: 'panel',
        itemId: 'deadlinesContainer',
        cls: 'devilry_discussionview_container'
    }]
});
