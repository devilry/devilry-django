Ext.define('devilry_nodeadmin.view.nodebrowser.NodeDetailsOverview', {
    extend: 'Ext.view.View',
    alias: 'widget.nodedetailsoverview',
    cls: 'devilry_nodeadmin_nodedetailsoverview bootstrap devilry_focuscontainer',
    padding: 20,
    tpl: [
        '<tpl for=".">',
            '<h1>', gettext( 'About' ), ' {short_name}</h1>',
            '<p class="muted">{long_name}</p>',
            '<div>{ subject_count } ', gettext( 'courses' ), '</div>',
            '<div>{ assignment_count } ', gettext( 'assignments' ), '</div>',
            '<hr />',
            '<tpl if="subjects.length">',
                '<h4>', gettext( "Subjects" ), ' <small>', gettext( 'on this level' ), '</small></h4>',
                '<ul>',
                    '<tpl for="subjects">',
                    '<li class="course"><a href="/devilry_subjectadmin/#/subject/{ id }/">{ long_name }</a></li>',
                    '</tpl>',
                '</ul>',
                '<div class="footer">',
                gettext( 'Follow these subject links to extend deadlines, alter group membership, and to get detailed summaries of particular students.' ),
                '</div>',
            '</tpl>',
        '</tpl>'
    ],

    itemSelector: 'li .course',

    store: 'NodeDetails'
});
