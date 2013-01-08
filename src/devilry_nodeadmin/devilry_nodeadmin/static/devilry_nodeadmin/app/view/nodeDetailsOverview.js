Ext.define('devilry_nodeadmin.view.nodeDetailsOverview', {
    extend: 'Ext.view.View',
    alias: 'widget.nodedetailsoverview',
    cls: 'bootstrap',
    tpl: [
        '<tpl for=".">',
        '<h1>About <i>{ short_name }</i></h1>',
        '<h3><i>{ long_name }</i></h3>',
        '<div>{ subject_count } emner</div>',
        '<div>{ assignment_count } oppgaver</div>',
        '<hr />',
        '<h4>Kurs <small>Nede ser du kursene som hører til dette nivået</small></h4>',
        '<dl>',
        '<tpl for="subjects">',
        '<li class="course"><a href="/devilry_subjectadmin/#/subject/{ id }/">{ long_name }</a></li>',
        '</tpl>',
        '</ul>',
        '<div style="">Lenkene til hver kurs tar deg et sted hvor du kan flytte fristene, endre gruppetilhørighet, ',
            'og </div>',
        '</tpl>'
    ],

    itemSelector: 'li .course',

    initComponent: function() {
        this.store = Ext.create( 'devilry_nodeadmin.store.NodeDetails' );
        this.store.proxy.url = Ext.String.format('/devilry_nodeadmin/rest/node/{0}/details', this.node_pk );
        this.callParent(arguments);
    }

});