Ext.define('subjectadmin.view.createnewassignment.CreateNewAssignment' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.createnewassignment',
    requires: [
        'themebase.layout.RightSidebar',
        'themebase.PrimaryButton'
    ],

    layout: 'rightsidebar',

    items: [{
        xtype: 'container',
        region: 'main',
        items: [{
            xtype: 'box',
            cls: 'sysadmin-messages box',
            html: Ext.String.format(
                '<h2 class="boxtitle">{0}</h2>',
                dtranslate('subjectadmin.createnewassignment.title')
            ),
        }, {
            margin: 40,
            xtype: 'createnewassignmentform'
        }]
    }, {
        xtype: 'box',
        region: 'sidebar',
        html: dtranslate('subjectadmin.createnewassignment.sidebarhelp')
    }]
});
