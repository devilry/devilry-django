Ext.define('devilry_student.view.browse.BrowseList' ,{
    extend: 'Ext.view.View',
    alias: 'widget.browselist',
    cls: 'devilry_student_browselist bootstrap',

    store: 'GroupedResults',
    autoScroll: true,
    layout: 'fit',
    padding: 20,

    tpl: [
        '<tpl for=".">',
            '<div class="subjectresults">',
                '<h2>{long_name}</h2>',
                '<tpl for="periods">',
                    '<h3>{long_name}</h3>',
                    '<table class="table table-striped table-bordered table-hover">',
                        '<tpl for="assignments">',
                            '<tpl for="groups">',
                                '<tr>',
                                    '<td>',
                                        '<a href="{[this.getFeedbackUrl(values)]}">{parent.long_name}</a>',
                                    '</td>',
                                    '<td style="width: 150px;">',
                                        '<tpl if="status === \'corrected\'">',
                                            '<strong class="grade">',
                                                '{feedback.grade}',
                                            '</strong> ',
                                            '<tpl if="feedback.is_passing_grade">',
                                                '<small class="passing_grade text-success">(',
                                                    gettext('Passed'),
                                                ')</small>',
                                            '<tpl else>',
                                                '<small class="failing_grade text-warning">(',
                                                    gettext('Failed'),
                                                ')</small>',
                                            '</tpl>',
                                        '<tpl else>',
                                            '<tpl if="status === \'waiting-for-deliveries\'">',
                                                '<em><small class="muted">', gettext('Waiting for deliveries'), '</small></em>',
                                            '<tpl elseif="status === \'waiting-for-feedback\'">',
                                                '<em><small class="muted">', gettext('Waiting for feedback'), '</small></em>',
                                            '<tpl else>',
                                                '<span class="label label-important">{status}</span>',
                                            '</tpl>',
                                        '</tpl>',
                                    '</td>',
                                '</tr>',
                            '</tpl>',
                        '</tpl>',
                    '</table>',
                '</tpl>',
            '</div>',
        '</tpl>', {
            getFeedbackUrl: function(group) {
                return Ext.String.format('#/group/{0}/{1}',
                    group.id,
                    group.feedback? group.feedback.delivery_id: '');
            },
            getFeedbackCls: function(feedback) {
                return feedback.is_passing_grade? 'text-success': 'text-warning';
            }
        }
    ],

    itemSelector: 'div.subjectresults'
});
