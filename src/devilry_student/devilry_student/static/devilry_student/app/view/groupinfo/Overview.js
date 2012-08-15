Ext.define('devilry_student.view.groupinfo.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.groupinfo',
    cls: 'devilry_student_groupinfo',

    /**
     * @cfg {Object} [group_id]
     */

    /**
     * @cfg {Object} [delivery_id]
     * ID of a delivery that should be highlighted on load.
     */

    frame: false,
    border: 0,
    bodyPadding: 0,

    layout: 'border',

    items: [{
        xtype: 'box',
        height: 'auto',
        region: 'north',
        padding: '20 20 0 20',
        itemId: 'titleBox',
        cls: 'bootstrap',
        tpl: [
            '<tpl if="groupinfo">',
                '<h1>{groupinfo.breadcrumbs.assignment.long_name}</h1>',
                '<p><small>',
                    '{groupinfo.breadcrumbs.subject.short_name}.',
                    '{groupinfo.breadcrumbs.period.short_name}.',
                    '{groupinfo.breadcrumbs.assignment.short_name}',
                '</small></p>',
            '<tpl else>',
                gettext('Loading ...'),
            '</tpl>'
        ]
    }, {
        xtype: 'container',
        region: 'west',
        autoScroll: true,
        width: 200,
        padding: 20,
        itemId: 'metadataContainer'
    }, {
        xtype: 'panel',
        region: 'center',
        bodyPadding: 20,
        autoScroll: true,
        itemId: 'deadlinesContainer',
        cls: 'devilry_discussionview_container'
    }]
});
