Ext.define('devilry_frontpage.view.frontpage.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.overview',
    cls: 'devilry_frontpage_overview',

    frame: false,
    border: 0,
    bodyPadding: 20,
    autoScroll: true,
    layout: 'column',

    items: [{
        xtype: 'box',
        html: 'Coming soon... Use the header to select your role for now.'
    }]
});
