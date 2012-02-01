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
            xtype: 'container',
            cls: 'centerbox sysadmin-messages',
            items: [{
                xtype: 'box',
                html: Ext.String.format(
                    '<h2 class="centertitle">{0}</h2>',
                    dtranslate('subjectadmin.createnewassignment.title')
                ),
            }, {
                cls: 'centerbody',
                xtype: 'createnewassignmentform'
            }]
        }]
    }, {
        xtype: 'box',
        region: 'sidebar',
        html: dtranslate('subjectadmin.createnewassignment.sidebarhelp')
    }]
});
