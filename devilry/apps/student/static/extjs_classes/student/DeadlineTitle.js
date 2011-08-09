Ext.define('devilry.student.DeadlineTitle', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.deadlinetitle',
    cls: 'widget-deadlinetitle',

    tpl: Ext.create('Ext.XTemplate',
        '<h1>{assignment_group__parentnode__parentnode__parentnode__long_name}</h1>',
        '<h2>{assignment_group__parentnode__parentnode__long_name}</h2>',
        '<h3>{assignment_group__parentnode__long_name} &mdash; deadline: {deadline:date}</h3>',
        '<tpl if="assignment_group__name">',
        '   {assignment_group__name}: ',
        '</tpl>',
        '<ul>',
        '<tpl for="assignment_group__candidates__identifier">',
        '   <li>{.}</li>',
        '</tpl>',
        '</ul>'
    )
});
