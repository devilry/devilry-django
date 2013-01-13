Ext.define('devilry_nodeadmin.view.nodebrowser.NodeDetailsOverview', {
    extend: 'Ext.view.View',
    alias: 'widget.nodedetailsoverview',
    cls: 'devilry_nodeadmin_nodedetailsoverview bootstrap',
    tpl: [
        '<tpl for=".">',
            '<h1>', gettext( 'Om' ), '<i>{ short_name }</i></h1>',
            '<h3>{ long_name }</h3>',
            '<div>{ subject_count } emner</div>',
            '<div>{ assignment_count } oppgaver</div>',
            '<hr />',
            '<tpl if="subjects.length">',
                '<h4>', gettext( "Kurs" ), ' <small>', gettext( 'som hører til dette nivået' ), '</small></h4>',
                '<ul>',
                    '<tpl for="subjects">',
                    '<li class="course"><a href="/devilry_subjectadmin/#/subject/{ id }/">{ long_name }</a></li>',
                    '</tpl>',
                '</ul>',
                '<div class="footer">',
                    gettext( 'Lenkene til disse kurs tar deg et sted der du kan flytte fristene, endre gruppetilhørighet, og se detaljene om en student.' ),
                '</div>',
            '</tpl>',
        '</tpl>'
    ],

    itemSelector: 'li .course',

    store: 'NodeDetails'
});