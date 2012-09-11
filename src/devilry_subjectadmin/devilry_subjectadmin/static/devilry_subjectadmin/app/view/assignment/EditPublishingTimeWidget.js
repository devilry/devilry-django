/**
 * A widget that shows if an assignment is published, when it was/is-to-be
 * published, and provides an edit button which a controller can use to
 * display widget to change the publishing_time.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditPublishingTimeWidget', {
    extend: 'devilry_extjsextras.EditableSidebarBox',
    alias: 'widget.editpublishingtime-widget',
    cls: 'devilry_subjectadmin_editpublishingtime_widget',
    bodyTpl: [
        '<p>',
            '<tpl if="text">',
                '<small>{text}</small>',
            '<tpl else>',
                '<tpl if="is_published">',
                    '<span class="success">{offset_from_now}</span>',
                '<tpl else>',
                    '<span class="danger">{offset_from_now}</span>',
                '</tpl>',
                ' <small class="muted">({publishing_time})</small>',
            '</tpl>',
        '</p>'
    ]
});
