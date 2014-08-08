Ext.define('devilry_student.view.browsegrouped.BrowseGrouped' ,{
    extend: 'Ext.view.View',
    alias: 'widget.browsegrouped',
    cls: 'devilry_student_browsegrouped bootstrap',

    store: 'GroupedResults',
    autoScroll: true,
    layout: 'fit',
    padding: 20,

    /**
     * @cfg {bool} [activeonly=false]
     * List active periods only?
     */
    activeonly: false,

    tpl: [
        '<h1>',
            '<tpl if="activeonly">',
                gettext('Active {period_term}'),
            '<tpl else>',
                gettext('History'),
            '</tpl>',
        '</h1>',
        '<hr/>',
        '<tpl for="subjects">',
            '<div class="subjectresults devilry_focuscontainer" style="padding: 20px; margin-bottom: 20px;">',
                '<h2>{data.long_name}</h2>',
                '<tpl for="data.periods">',
                    '<h3>{long_name}</h3>',
                    '<tpl if="is_relatedstudent">',
                        '<tpl if="qualifiesforexams == true">',
                            '<p><span class="label label-success">',
                                gettext('Qualified for final exams'),
                            '</span></p>',
                        '<tpl elseif="qualifiesforexams == false">',
                            '<p><span class="label label-important">',
                                gettext('Not qualified for final exams'),
                            '</span></p>',
                        '</tpl>',
                    '<tpl else>',
                        '<p class="alert">',
                            '<strong>', gettext('WARNING'), ':</strong> ',
                            gettext('You are not registered as a student on {[this.getPeriodShortNameHack(parent)]}.{short_name}.'),
                        '</p>',
                    '</tpl>',
                    '<table class="table table-striped table-bordered table-hover">',
                        '<tpl for="assignments">',
                            '<tpl for="groups">',
                                '<tr>',
                                    '<td>',
                                        '<a href="{[this.getFeedbackUrl(values)]}">{parent.long_name}</a>',
                                    '</td>',
                                    '<td style="width: 200px;">',
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
                                                '<em><small class="muted">',
                                                    gettext('Waiting for deliveries, or for deadline to expire'),
                                                '</small></em>',
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
            getPeriodShortNameHack: function(parentobjorarray) {
                // WARNING: THIS IS A HACK/WORKAROUND
                // This is a hack to work around an issue in Sencha
                // Touch version 4.1. See:
                // https://github.com/devilry/devilry-django/issues/436
                //
                // When we have updated to ExtJS 4.2.x, we should be able to
                // go back to using ``{parent.data.short_name}``.
                var parentobj = parentobjorarray;
                if(Ext.isArray(parentobjorarray)) {
                    parentobj = parentobjorarray[parentobjorarray.length-1];
                }
                return parentobj.data.short_name;
            },
            getFeedbackCls: function(feedback) {
                return feedback.is_passing_grade? 'text-success': 'text-warning';
            }
        }
    ],

    itemSelector: 'div.subjectresults',

    collectData: function(records, startIndex) {
        return {
            subjects: records,
            period_term: gettext('period'),
            activeonly: this.activeonly
        };
    }
});
