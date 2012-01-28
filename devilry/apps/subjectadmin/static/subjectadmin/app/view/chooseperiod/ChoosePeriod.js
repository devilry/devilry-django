Ext.define('subjectadmin.view.chooseperiod.ChoosePeriod' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.chooseperiod',
    requires: [
        'themebase.layout.RightSidebar'
    ],

    layout: 'rightsidebar',

    items: [{
        xtype: 'container',
        region: 'main',
        items: [{
            xtype: 'box',
            cls: 'sysadmin-messages box',
            html: Ext.String.format('<h2 class="boxtitle">{0}</h2>', dtranslate('subjectadmin.chooseperiod.title')),
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
        region: 'sidebar',
        html: dtranslate('subjectadmin.chooseperiod.sidebarhelp')
    }]
});
