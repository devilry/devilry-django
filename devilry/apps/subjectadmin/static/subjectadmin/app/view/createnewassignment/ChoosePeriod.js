Ext.define('subjectadmin.view.createnewassignment.ChoosePeriod' ,{
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
            xtype: 'container',
            cls: 'centerbox',
            items: [{
                xtype: 'box',
                html: Ext.String.format('<h2 class="centertitle">{0}</h2>', dtranslate('subjectadmin.chooseperiod.title')),
            }, {
                xtype: 'container',
                cls: 'centerbody',
                items: [{
                    xtype: 'activeperiodslist',
                }, {
                    xtype: 'nextbutton',
                    margin: {top: 10}
                }]
            }]
        }]
    }, {
        xtype: 'box',
        region: 'sidebar',
        html: dtranslate('subjectadmin.chooseperiod.sidebarhelp')
    }]
});
