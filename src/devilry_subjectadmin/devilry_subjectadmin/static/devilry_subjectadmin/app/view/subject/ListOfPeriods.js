/**
 * List of periods within a subject.
 */
Ext.define('devilry_subjectadmin.view.subject.ListOfPeriods', {
    extend: 'Ext.view.View',
    alias: 'widget.listofperiods',
    cls: 'listofperiods bootstrap',
    store: 'Periods',

    tpl: [
        '<ul>',
            '<tpl for=".">',
                '<li class="period">',
                    '<a href="#/{parentnode__short_name}/{short_name}/">{long_name}</a>',
                '</li>',
            '</tpl>',
        '<ul>'
    ],
    itemSelector: 'li.period',
});
