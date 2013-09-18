Ext.define('devilry_nodeadmin.view.aggregatedstudentview.AggregatedStudentInfoOverview' ,{
  extend: 'Ext.container.Container',
  alias: 'widget.aggregatedstudentinfo',
  cls: 'bootstrap',
  title: 'Aggregated Student Info',

  layout: 'fit',
  padding: '40',
  autoScroll: true,

  items: [{
    xtype: 'box',
    itemId: 'AggregatedStudentInfoBox',
    //html: '<h1> Hello World </h1>',
    tpl: ['<h1>Aggregert Studentinformasjon</h1>',
          '<h2>{data.user.displayname} / {data.user.username}</h2>',
              '<tpl for="data.grouped_by_hierarky">',
                      '<p> {long_name} </p>',
                      '<tpl for="periods">',
                          '<p> {long_name} </p>',
                          '<tpl for="assignments">',
                              '<p> {long_name} </p>',
                              '<tpl for="groups">',
                                  '<p> {status} </p>',
                                  '<tpl if="active_feedback">',
                                      '<tpl if="active_feedback.feedback.is_passing_grade">',
                                          '<p> Approved </p>',
                                      '<tpl else>',
                                          '<p> Not Approved </p>',
                                      '</tpl>',
                                  '</tpl>',
                              '</tpl>',
                          '</tpl>',
                      '</tpl>', 
               '</tpl>',
              {

                help: function(rec) {
                  console.log("TPL: " + rec);
                  
                }

                
                
              }]
    
  }]

});
