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
                translate('subjectadmin.createnewassignment.title')
            ),
        }, {
            xtype: 'container',
            margin: 40,
            items: [{
                xtype: 'createnewassignmentform',
            }, {
                xtype: 'primarybutton',
                margin: {top: 10},
                text: translate('themebase.create')
            }]
        }]
    }, {
        xtype: 'box',
        region: 'sidebar',
        html: translate('subjectadmin.createnewassignment.sidebarhelp')
    }]
});
