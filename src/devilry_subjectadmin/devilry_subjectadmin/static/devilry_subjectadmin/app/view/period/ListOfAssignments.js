/**
 * List of assignments within a period.
 */
Ext.define('devilry_subjectadmin.view.period.ListOfAssignments', {
    extend: 'Ext.view.View',
    alias: 'widget.listofassignments',
    cls: 'devilry_listofassignments bootstrap',
    store: 'Assignments',

    tpl: [
        '<ul>',
            '<tpl for=".">',
                '<li class="devilry_assignment"><p>',
                    '<a href="#/assignment/{id}/">{long_name}</a>',
                '</p></li>',
            '</tpl>',
        '<ul>'
    ],
    itemSelector: 'li.devilry_assignment'
});
