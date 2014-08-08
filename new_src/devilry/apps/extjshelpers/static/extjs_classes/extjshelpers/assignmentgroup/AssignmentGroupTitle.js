Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupTitle', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.assignmentgrouptitle',
    cls: 'widget-assignmentgrouptitle section pathheading bootstrap',

    tpl: Ext.create('Ext.XTemplate',
        '<h1 style="margin: 0; line-height: 25px;"><small>{parentnode__parentnode__parentnode__short_name}.{parentnode__parentnode__short_name}.</small>{parentnode__long_name}</h1>',
        '<tpl if="name">',
            '{name}: ',
        '</tpl>',
        '<ul class="names" style="margin: 0;">',
            '<tpl for="candidates">',
                '<li>{identifier} <tpl if="full_name">({full_name})</tpl></li>',
            '</tpl>',
        '</ul>',
        '<tpl if="canExamine">',
            '<tpl if="parentnode__anonymous == false">',
                '<small><a href="mailto:',
                    '<tpl for="candidates">',
                        '{email}<tpl if="xindex &lt; xcount">,</tpl>',
                    '</tpl>',
                '?subject={parentnode__parentnode__parentnode__short_name}.{parentnode__parentnode__short_name}.{parentnode__short_name}',
                '&body={url}',
                '">',
                'Send email</a></small>',
            '</tpl>',
        '</tpl>'
    )
});
