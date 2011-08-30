Ext.define('devilry.student.DeadlineTitle', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.deadlinetitle',
    cls: 'widget-deadlinetitle',

    tpl: Ext.create('Ext.XTemplate',
        '<h1>{parentnode__parentnode__parentnode__long_name}</h1>',
        '<h2>{parentnode__parentnode__long_name}</h2>',
        '<h3>{parentnode__long_name} &mdash; deadline: DEADLINE </h3>',
        '<tpl if="name">',
        '   {name}: ',
        '</tpl>',
        '<ul>',
        '<tpl for="candidates__identifier">',
        '   <li>{.}</li>',
        '</tpl>',
        '</ul>'
    )
});
