Ext.define('devilry_nodeadmin.view.nodeDetailsOverview', {
    extend: 'Ext.view.View',
    alias: 'widget.nodedetailsoverview',
    cls: 'secondary',
    tpl: [
        '<tpl for=".">',
            '<h1>Om <i>{ short_name }</i></h1>',
            '<h3 style="font-style: italic;">{ long_name }</h3>',
            '<div>{ subject_count } emner</div>',
            '<div>{ assignment_count } oppgaver</div>',
            '<hr />',
            '<tpl if="subjects.length">',
                '<h4>Kurs <small> som hører til dette nivået</small></h4>',
                '<ul>',
                    '<tpl for="subjects">',
                    '<li class="course"><a href="/devilry_subjectadmin/#/subject/{ id }/">{ long_name }</a></li>',
                    '</tpl>',
                '</ul>',
                '<div class="footer">Lenkene til disse kurs tar deg et sted der du kan flytte fristene, endre gruppetilhørighet, ',
                    'og se detaljene om en student.</div>',
            '</tpl>',
        '</tpl>'
    ],

    itemSelector: 'li .course',

    initComponent: function() {
        this.store = Ext.create( 'devilry_nodeadmin.store.NodeDetails' );
        this.store.proxy.url = Ext.String.format('/devilry_nodeadmin/rest/node/{0}/details', this.node_pk );
        this.callParent(arguments);
    }

});