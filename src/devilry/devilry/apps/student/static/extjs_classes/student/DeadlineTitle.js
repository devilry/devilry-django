Ext.define('devilry.student.DeadlineTitle', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.deadlinetitle',
    cls: 'widget-deadlinetitle',

    tpl: Ext.create('Ext.XTemplate',
        '<div class="section pathheading">',
            '<h1><small>{parentnode__parentnode__parentnode__short_name}.{parentnode__parentnode__short_name}.</small>{parentnode__long_name}</h1>',
            '<div class="deadline"><em>', gettext('deadline'), ':</em> {latest_deadline:date}</div>',
            '<tpl if="name">',
                '<div class="groupname">{name}:</div> ',
            '</tpl>',
            '<ul class="listofcandidates">',
            '<tpl for="candidates__identifier">',
            '   <li>{.}</li>',
            '</tpl>',
            '</ul>',
        '</div>'
    )
});
