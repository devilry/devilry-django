Ext.define('devilry_nodeadmin.view.aggregatedstudentview.AggregatedStudentInfoOverview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.aggregatedstudentinfo',
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
