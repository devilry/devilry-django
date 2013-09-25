Ext.define('devilry_nodeadmin.view.aggregatedstudentview.AggregatedStudentInfoOverview' ,{
  extend: 'Ext.container.Container',
  alias: 'widget.aggregatedstudentinfo',
  cls: 'bootstrap',
  title: 'Aggregated Student Info',

  //layout: 'fit',
  padding: '40',
  autoScroll: true,

  items: [{
      xtype: 'container',
      layout: 'column',
      items: [{
          xtype: 'box',
          itemId: 'headerBox',
          columnWidth: 1.0,
          tpl: [
              '<h1 style="margin-top: 0;">', gettext('Student Information'), '</h1>',
              '<dl>',
                '<dt>', gettext('Name') ,'</dt>',
                '<dd>',
                    '<tpl if="data.user.full_name">',
                        '{data.user.full_name}',
                    '<tpl else>',
                        '<em class="text-warning">', gettext('Name missing'), '</em>',
                    '</tpl>',
                    '{data.user.name}',
                '<dd>',
                '<dt>', gettext('Username') ,'</dt>',
                '<dd>{data.user.username}<dd>',
                '<dt>', gettext('Email') ,'</dt>',
                '<dd>{data.user.email}<dd>',
              '</dl>'
          ]
      }, {
          xtype: 'container',
          width: 320,
          items: [{
              xtype: 'box',
              cls: 'bootstrap',
              margin: '0 0 4px 0',
              html: [
                  '<strong>',
                      gettext('Find details about another student:'),
                  '</strong>'
                  ].join('')
          }, {
              xtype: 'autocompleteuserwidget',
              itemId: 'userSearchBox',
              fieldLabel: '',
              emptyText: gettext('Search by name, username or email...'),
              width: 300
          }]
      }]
  }, {
    xtype: 'box',
    itemId: 'aggregatedStudentInfoBox',
    tpl: [
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
                              '<tpl for="groups">',
                                  '<td> <a href="{[this.getGroupUrl(parent, values)]}">{parent.long_name}</a></td>',
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

                getGroupUrl: function(assignment, group) {
                    return Ext.String.format('{0}/devilry_subjectadmin/#/assignment/{1}/@@manage-students/@@select/{2}',
                                             window.DevilrySettings.DEVILRY_URLPATH_PREFIX,
                                             assignment.id, group.id);
                }

                
                
              }]
    
  }]

});
