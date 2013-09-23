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
    tpl: ['<div class=devilry_focuscontainer style="padding: 20px; margin-bottom: 20px;">', '<h1>', gettext('Aggregated Student Information'), '</h1>',
          '<h3>{data.user.displayname}</h3> <h4>{data.user.username} / {data.user.email}</h4>',
          '</div>',
              '<tpl for="data.grouped_by_hierarky">',
                    '<div class="devilry_focuscontainer" style="padding: 20px; margin-bottom: 20px;">',
                      '<h2> {long_name} </h2>',
                      '<tpl for="periods">',
                          '<h3> {long_name} </h3>',
                          '<p>',
                          '<tpl if="is_relatedstudent">',
                              '<span class="label label-success" style="margin: 0 10px 0 0;">', gettext('Registred as student on period'), '</span>',
                          '<tpl else>',
                              '<span class="label label-important" style="margin: 0 10px 0 0;">', gettext('Not registred as student on period'), '</span>',
                          '</tpl>',
                          '<tpl if="qualified_forexams === null">',
                              '<span class="label">', gettext('No information on exam qualification'), '</span>',
                          '<tpl elseif="qualified_forexams">',
                              '<span class="label label-success">', gettext('Qualified for final exam'), '</span>',
                          '<tpl else>',
                              '<span class="label label-important">', gettext('Not Qualified for final exam'), '</span>',
                          '</tpl>',
                          '</p>',
                          '<table class="table table-striped table-bordered table-hover">',
          '<tr class="info"> <td>', gettext('Assignment'), '</td> <td>', gettext('Feedback Status'), '</td>', '</tr>',
                          '<tpl for="assignments">',
                              '<tr>',
                              '<td> {long_name} </td>',
                              '<tpl for="groups">',
                                  '<td style="width: 200px;">',
                                  '<tpl if="status === \'corrected\'">',
                                      '<strong class="grade">',
                                          '{active_feedback.feedback.grade}',
                                      '</strong> ',
                                      '<tpl if="active_feedback.feedback.is_passing_grade">',
                                          '<span class="label label-success">', gettext('Passed'), '</span>',
                                      '<tpl else>',
                                          '<span class="label label-error">', gettext('Failed'), '</span>',
                                      '</tpl>',
                                  '<tpl elseif="status === \'waiting-for-deliveries\'">',
                                      '<em><small class="muted">',
                                      gettext('Waiting for deliveries, or for deadline to expire'),
                                      '</small></em>',
                                  '<tpl elseif="status === \'waiting-for-feedback\'">',
                                      '<em><small class="muted">', gettext('Waiting for feedback'), '</small></em>',
                                  '</tpl>',
                                  '</td>',

                              '</tpl>',
                              '</tr>',
                          '</tpl>',
                      '</table>',
                      '</tpl>',
                    '</div>', 
                '</tpl>',

              {

                help: function(rec) {
                  console.log("TPL: " + rec);
                  
                }

                
                
              }]
    
  }]

});
