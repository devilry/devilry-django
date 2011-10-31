Ext.define('devilry.student.DeadlineTitle', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.deadlinetitle',
    cls: 'widget-deadlinetitle',

    tpl: Ext.create('Ext.XTemplate',
        '<div class="section treeheading">',
        '<h1>{parentnode__long_name}</h1>',
        '<h2>{parentnode__parentnode__long_name}</h2>',
        '<h3>{parentnode__parentnode__parentnode__long_name}</h3>',
        '<div class="deadline"><em>deadline:</em> {latest_deadline:date}</div>',
        '<tpl if="name">',
        '   {name}: ',
        '</tpl>',
        '<ul>',
        '<tpl for="candidates__identifier">',
        '   <li>{.}</li>',
        '</tpl>',
        '</ul>',
        '</div>'
    )
});
