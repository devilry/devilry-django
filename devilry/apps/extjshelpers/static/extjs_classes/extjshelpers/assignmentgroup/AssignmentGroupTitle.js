Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupTitle', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.assignmentgrouptitle',
    cls: 'widget-assignmentgrouptitle section treeheading',

    tpl: Ext.create('Ext.XTemplate',
        '<h1>{parentnode__parentnode__parentnode__long_name}</h1>',
        '<h2>{parentnode__parentnode__long_name}</h2>',
        '<h3>{parentnode__long_name}</h3>',
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
