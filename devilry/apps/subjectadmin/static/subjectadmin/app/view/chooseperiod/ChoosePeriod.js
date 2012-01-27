Ext.define('subjectadmin.view.chooseperiod.ChoosePeriod' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.chooseperiod',
    requires: [
        'subjectadmin.layout.RightSidebar'
    ],

    layout: 'rightsidebar',

    items: [{
        xtype: 'container',
        region: 'main',
        items: [{
            xtype: 'box',
            cls: 'sysadmin-messages box',
            html: Ext.String.format('<h2 class="boxtitle">{0}</h2>', translate('subjectadmin.chooseperiod.title')),
        }, {
            xtype: 'container',
            margin: 40,
            items: [{
                xtype: 'activeperiodslist',
            }, {
                xtype: 'nextbutton',
                margin: {top: 10}
            }]
        }]
    }, {
        xtype: 'box',
        border: 'false',
        region: 'sidebar',
        width: 400,
        html: translate('subjectadmin.chooseperiod.sidebarhelp')
    }]
});
