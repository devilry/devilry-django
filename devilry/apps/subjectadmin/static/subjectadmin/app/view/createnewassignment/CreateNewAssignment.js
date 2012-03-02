Ext.define('subjectadmin.view.createnewassignment.CreateNewAssignment' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.createnewassignment',
    requires: [
        'themebase.layout.RightSidebar',
        'themebase.PrimaryButton'
    ],

    layout: 'border',
    border: 0,
    bodyPadding: 40,

    items: [{
        xtype: 'box',
        region: 'north',
        height: 50,
        html: Ext.String.format(
            '<h2>{0}</h2>',
            dtranslate('subjectadmin.createnewassignment.title')
        ),
    }, {
        region: 'center',
        autoScroll: true,
        border: 0,
        items: { // Note: We wrap this in an extra container to avoid that the create button ends up at the bottom of the screen
            xtype: 'container',
            xtype: 'createnewassignmentform'
        }
    }]
});
