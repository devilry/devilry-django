Ext.define('devilry_examiner.view.dashboard.Dashboard' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.dashboard',
    cls: 'dashboard',

    //requires: [
        //'devilry_examiner.view.dashboard.'
    //],

    layout: 'fit',
    padding: '40',
    autoScroll: true,

    items: [{
        xtype: 'box',
        html: 'Hello world'
    }]
});
