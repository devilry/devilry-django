Ext.define('devilry_nodeadmin.view.nodebrowser.NodeDetailsOverview', {
    extend: 'Ext.Component',
    alias: 'widget.nodedetailsoverview',
    cls: 'devilry_nodeadmin_nodedetailsoverview bootstrap devilry_focuscontainer',
    padding: 20,

    requires: [
        'devilry_nodeadmin.utils.UrlLookup'
    ],

    tpl: [
        '<h1>{node.long_name}</h1>',
        '<p class="muted">',
            '<span class="subject_count">{node.subject_count} ', gettext( 'courses' ), '</span>, ',
            '<span class="assignment_count">{node.assignment_count} ', gettext( 'assignments' ), '</span>',
            '</p>',
        '<hr />',
        '<tpl if="node.subjects.length">',
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
                '<tpl for="node.subjects">',
                    '<li class="course"><a href="/devilry_subjectadmin/#/subject/{ id }/">{ long_name }</a></li>',
                '</tpl>',
            '</ul>',
        '</tpl>',

        '<tpl if="childnodes.length">',
            '<h2>',
                gettext('Childnodes'),
            '</h2>',
            '<ul>',
                '<tpl for="childnodes">',
                    '<li>',
                        '<a href="/devilry_nodeadmin/#/node/{ id }">{ long_name }</a>',
                    '</li>',
                '</tpl>',
            '</ul>',
        '</tpl>',

        '<tpl if="noChildren">',
            '<p class="muted">',
                gettext('There is nothing here.'),
            '</p>',
        '</tpl>',

        '<h2>',
            gettext('Add courses or nodes?'),
        '</h2>',
        '</p>',
            gettext('Adding course or nodes requires superuser permissions. If you have superuser permissions, you will find the superuser role on the frontpage.'),
        '</p>', {
            getQualifiedForExamsSummaryUrl: function(node_id) {
                return devilry_nodeadmin.utils.UrlLookup.qualifiedForExamsSummary(node_id);
            }
        }
    ]
});
