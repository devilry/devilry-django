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
    autoScroll: true,

    layout: 'column',

    items: [{
        xtype: 'container',
        columnWidth: 0.75,
        padding: 20,
        items: [{
            xtype: 'box',
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
            xtype: 'panel',
            itemId: 'deadlinesContainer',
            cls: 'devilry_discussionview_container'
        }]
    }, {
        xtype: 'container',
        columnWidth: 0.25,
        padding: 20,
        itemId: 'metadataContainer'
    }]
});
