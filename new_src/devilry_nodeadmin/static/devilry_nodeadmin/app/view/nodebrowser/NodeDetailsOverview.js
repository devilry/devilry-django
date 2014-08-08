Ext.define('devilry_nodeadmin.view.nodebrowser.NodeDetailsOverview', {
    extend: 'Ext.Component',
    alias: 'widget.nodedetailsoverview',
    cls: 'devilry_nodeadmin_nodedetailsoverview bootstrap devilry_focuscontainer',
    padding: 20,

    requires: [
        'devilry_nodeadmin.utils.UrlLookup'
    ],

    tpl: [
        '<h1>{long_name}</h1>',
        '<span class="subject_count">{ subject_count } ', gettext( 'courses' ), '</span>, ',
        '<span class="assignment_count">{ assignment_count } ', gettext( 'assignments' ), '</span>',
        '<hr />',
        '<tpl if="subjects.length">',
            '<h2>', gettext('Tools'), '</h2>',
            '<ul class="unstyled devilry_nodeadmin_toolslist">',
                '<li>',
                    '<strong><a href="{[this.getQualifiedForExamsSummaryUrl(values.id)]}">',
                        gettext('Qualified for final exams'),
                    '</strong></a>',
                    '<small class="muted"> - ',
                        gettext('View, print and browse students "qualified for final exams"-status.'),
                    '</small>',
                '</li>',
            '</ul>',
            '<h2>', gettext( "Subjects" ), ' <small>', gettext( 'on this level' ), '</small></h2>',
            '<p class="muted"><small>',
                interpolate(gettext('Follow these links to get access to all the details available to %(subject_term)s administrators. This includes the ability to extend deadlines, view detailed information about students and their feedback, and much more.'), {
                    subject_term: gettext('subject')
                }, true),
            '</small></p>',
            '<ul>',
                '<tpl for="subjects">',
                '<li class="course"><a href="/devilry_subjectadmin/#/subject/{ id }/">{ long_name }</a></li>',
                '</tpl>',
            '</ul>',
        '<tpl else>',
            '<p class="muted">',
                interpolate(gettext('No %(subjects_term)s on this level. If there are any %(nodes_term)s below this level, they are listed in the menu on your left hand side.'), {
                    subjects_term: gettext('subjects'),
                    nodes_term: gettext('nodes')
                }, true),
            '</p>',
        '</tpl>', {
            getQualifiedForExamsSummaryUrl: function(node_id) {
                return devilry_nodeadmin.utils.UrlLookup.qualifiedForExamsSummary(node_id);
            }
        }
    ]
});
