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
                '<li class="assignment">',
                    '<a href="#/assignment/{id}/">{long_name}</a>',
                '</li>',
            '</tpl>',
        '<ul>'
    ],
    itemSelector: 'li.assignment',
});
