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
        //frame: false,
        //border: 0,
        itemId: 'deadlinesContainer',
        layout: {
            // layout-specific configs go here
            type: 'accordion',
            titleCollapse: true,
            animate: true,
            multi: true
            //hideCollapseTool: true
            //activeOnTop: true
        }
        //defaults: {
            //// applied to each contained panel
            //bodyStyle: 'padding:15px'
        //},
    }]
});
