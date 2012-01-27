Ext.define('subjectadmin.view.chooseperiod.ChoosePeriod' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.chooseperiod',

    layout: 'rightsidebar',

    items: [{
        xtype: 'container',
        region: 'main',
        items: [{
            xtype: 'box',
            cls: 'sysadmin-messages box',
            html: [
                '<h2 class="boxtitle">Choose period</h2>',
            ].join('')
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
        html: 'Please choose a period and click <em>Next</em>.'
    }]
});
