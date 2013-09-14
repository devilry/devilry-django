Ext.define('devilry_nodeadmin.view.aggregatedstudentview.AggregatedStudentInfoOverview' ,{
  extend: 'Ext.container.Container',
  alias: 'widget.aggregatedstudentinfo',
  cls: 'dashboard',
  title: 'Aggregated Student Info',
  
  layout: 'fit',
  padding: '40',
  autoScroll: true,
  
  items: [{
    xtype: 'box',
    html: '<h1> Hello World </h1>',
    tpl: ['<h1>Hello world</h1>',]
  }]

});
